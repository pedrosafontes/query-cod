from functools import singledispatchmethod
from typing import cast

import queries.services.ra.ast as ra
import sqlglot.expressions as sql
from queries.services.types import (
    RelationalSchema,
    SQLQuery,
    ra_to_sql_bin_bool_ops,
    ra_to_sql_comparisons,
)
from sqlglot.expressions import Exists, Expression, Select, column, select, subquery, table_

from ..ast import RAQuery, Relation
from ..scope.schema import SchemaInferrer
from .renamer import RAExpressionRenamer


class RAtoSQLTranspiler:
    def __init__(self, schema: RelationalSchema, bag: bool = False):
        self._schema_inferrer = SchemaInferrer(schema)
        self._bag = bag

    def transpile(self, query: RAQuery) -> SQLQuery:
        transpiled = self._transpile(query)
        return transpiled

    @singledispatchmethod
    def _transpile(self, query: RAQuery) -> SQLQuery:
        raise NotImplementedError(f'No transpiler for {type(query).__name__}')

    @_transpile.register
    def _(self, rel: ra.Relation, alias: str | None = None) -> Select:
        return select('*').from_(table_(rel.name, alias=alias))

    @_transpile.register
    def _(self, proj: ra.Projection) -> Select:
        query = self._transpile_select(proj.operand)

        existing_exprs = cast(list[Expression], query.expressions)
        expressions: list[Expression] = []

        for attr in proj.attributes:
            matched_expr: Expression | None = None

            if attr.relation is None:
                matched_expr = next(
                    (expr for expr in existing_exprs if expr.alias and expr.alias == attr.name),
                    None,
                )

            expressions.append(matched_expr or self._transpile_attribute(attr))

        query.select(*expressions, append=False, copy=False)

        if not self._bag:
            query.distinct(copy=False)

        return query

    @_transpile.register
    def _(self, selection: ra.Selection) -> Select:
        query = self._transpile_select(selection.operand)
        condition = self._transpile_condition(selection.condition)
        if query.args.get('group') or self._refers_to(condition, query.expressions):
            return query.having(condition)
        else:
            return query.where(condition)

    def _refers_to(self, condition: Expression, exprs: list[Expression]) -> bool:
        idents = condition.find_all(sql.Identifier)
        return any([ident.this == expr.alias for ident in idents for expr in exprs])

    def _transpile_condition(self, cond: ra.BooleanExpression) -> Expression:  # type: ignore[return]
        match cond:
            case ra.BinaryBooleanExpression():
                left = self._transpile_condition(cond.left)
                right = self._transpile_condition(cond.right)
                sql_operator = ra_to_sql_bin_bool_ops[type(cond)]
                return sql_operator(left, right)
            case ra.Not():
                return sql.not_(self._transpile_condition(cond.expression))
            case ra.Comparison():
                left = self._transpile_comparison_value(cond.left)
                right = self._transpile_comparison_value(cond.right)
                sql_comparison = ra_to_sql_comparisons[type(cond)]
                return sql_comparison(this=left, expression=right)
            case ra.Attribute() as attr:
                return sql.EQ(
                    this=self._transpile_attribute(attr), expression=sql.Boolean(this=True)
                )

    @_transpile.register
    def _(self, div: ra.Division) -> Select:
        # Get tables with aliases
        dividend, dividend_alias = self._transpile_relation(div.dividend, 'dividend')
        dividend_sub, dividend_sub_alias = self._transpile_relation(div.dividend, 'missing_divisor')

        output_attrs = [a.name for a in self._schema_inferrer.infer(div).attrs]
        divisor_attrs = [a.name for a in self._schema_inferrer.infer(div.divisor).attrs]

        # Create join conditions between the two dividend instances
        match_conditions = [
            sql.EQ(
                this=column(attr, table=dividend_sub_alias),
                expression=column(attr, table=dividend_alias),
            )
            for attr in output_attrs
        ]

        # For each dividend tuple:
        # 1. Find all divisor tuples associated with it
        found_divisors = dividend_sub.select(*divisor_attrs, append=False).where(*match_conditions)
        # 2. Check if there are any divisor tuples that are not associated with it
        divisor = self._transpile(div.divisor)
        missing_divisors = divisor.except_(found_divisors)

        candidates = dividend.select(*output_attrs, append=False).distinct()
        return candidates.where(sql.not_(Exists(this=missing_divisors)))

    def _transpile_attribute(self, attr: ra.Attribute) -> Expression:
        return column(attr.name, table=attr.relation)

    def _transpile_comparison_value(self, comparison: ra.ComparisonValue) -> Expression:
        if isinstance(comparison, ra.Attribute):
            return self._transpile_attribute(comparison)
        elif isinstance(comparison, bool):
            return sql.Boolean(this=comparison)
        elif isinstance(comparison, str):
            return sql.Literal.string(comparison)
        else:
            return sql.Literal.number(comparison)

    @_transpile.register
    def _(self, op: ra.SetOperator) -> SQLQuery:
        left = self._transpile(op.left)
        right = self._transpile(op.right)

        match op.kind:
            case ra.SetOperatorKind.UNION:
                return left.union(right)
            case ra.SetOperatorKind.INTERSECT:
                return left.intersect(right)
            case ra.SetOperatorKind.DIFFERENCE:
                return left.except_(right)
            case ra.SetOperatorKind.CARTESIAN:
                left = self._transpile_select(op.left)
                match op.right:
                    case Relation() as relation:
                        return left.join(relation.name, join_type='CROSS')
                    case ra.Rename(Relation() as relation, alias=alias):
                        return left.join(relation.name, join_type='CROSS', join_alias=alias)
                    case _:
                        # right is a derived relation
                        return left.join(right, join_type='CROSS', join_alias='r')

    @_transpile.register
    def _(self, join: ra.Join) -> Select:
        left, left_alias = self._transpile_relation(join.left, alias='l')

        match join.kind:
            case ra.JoinKind.SEMI | ra.JoinKind.ANTI:
                right, right_alias = self._transpile_relation(join.right, 'r')
                common = self._common_attrs(join.left, join.right)

                condition: Expression = Exists(
                    this=right.where(
                        *[
                            sql.EQ(
                                this=column(name, table=left_alias),
                                expression=column(name, table=right_alias),
                            )
                            for name in common
                        ]
                    )
                )

                if join.kind == ra.JoinKind.ANTI:
                    condition = sql.not_(condition)

                return left.where(condition)
            case _:
                using = []
                if join.kind != ra.JoinKind.NATURAL:
                    using = self._common_attrs(join.left, join.right)

                if isinstance(join.right, Relation):
                    # join.right is a base table
                    return left.join(join.right.name, join_type=join.kind.value, using=using)
                else:
                    # right is a derived relation
                    right_query = self._transpile(join.right)
                    return left.join(
                        right_query, join_type=join.kind.value, join_alias='r', using=using
                    )

    @_transpile.register
    def _(self, join: ra.ThetaJoin) -> Select:
        left, left_alias = self._transpile_relation(join.left, 'l')

        # rename the attributes in the left relation to use the alias
        left_schema = self._schema_inferrer.infer(join.left).schema
        renamings: dict[str, str] = {}
        for table in left_schema.keys():
            if table:
                renamings[table] = left_alias

        right: sql.ExpOrStr
        if isinstance(join.right, Relation):
            # right is a base table
            right = join.right.name
            right_alias = None
        else:
            # right is a derived relation
            right = self._transpile(join.right)
            right_alias = 'r'

            # rename the attributes in the right relation to use the alias
            right_schema = self._schema_inferrer.infer(join.right).schema
            for table in right_schema.keys():
                if table:
                    renamings[table] = right_alias

        renamed_condition = RAExpressionRenamer(renamings).rename_condition(join.condition)
        condition = self._transpile_condition(renamed_condition)
        return left.join(right, join_alias=right_alias, on=condition)

    @_transpile.register
    def _(self, agg: ra.GroupedAggregation) -> Select:
        query = self._transpile_select(agg.operand)

        if not isinstance(agg.operand, Relation):
            query = subquery(query, 'sub')

        attrs = [self._transpile_attribute(attr) for attr in agg.group_by]

        return (
            query.select(*attrs, append=False)
            .select(*[self._transpile_aggregation(a) for a in agg.aggregations])
            .group_by(*attrs)
        )

    def _transpile_aggregation(self, agg: ra.Aggregation) -> sql.ExpOrStr:
        return f'{agg.aggregation_function}({agg.input}) AS {agg.output}'

    @_transpile.register
    def _(self, top_n: ra.TopN) -> Select:
        query = self._transpile_select(top_n.operand)
        return query.limit(top_n.limit).order_by(self._transpile_attribute(top_n.attribute).desc())

    @_transpile.register
    def _(self, rename: ra.Rename) -> Select:
        match rename.operand:
            case ra.Relation() as relation:
                # rename is a base table
                return cast(Select, self._transpile(relation, alias=rename.alias))
            case _:
                # rename is a derived relation
                query = self._transpile(rename.operand)
                return subquery(query, rename.alias).select('*')

    def _transpile_relation(self, relation: RAQuery, alias: str) -> tuple[Select, str]:
        select = self._transpile_select(relation)
        match relation:
            case Relation():
                # relation is a base table
                return select, relation.name
            case ra.Rename(Relation(), alias=alias):
                # relation is a renamed base table
                return select, alias
            case ra.Rename():
                return select, relation.alias
            case _:
                # relation is a derived relation; therefore, it needs to be aliased
                return subquery(select, alias).select('*'), alias

    def _transpile_select(self, query: RAQuery) -> Select:
        sql_query = self._transpile(query)
        if not isinstance(sql_query, Select):
            sql_query = subquery(sql_query, 'set_op').select('*')

        return sql_query

    def _common_attrs(self, left: RAQuery, right: RAQuery) -> list[str]:
        l_output = self._schema_inferrer.infer(left)
        r_output = self._schema_inferrer.infer(right)

        l_names = {attr.name for attr in l_output.attrs}
        r_names = {attr.name for attr in r_output.attrs}
        return list(l_names & r_names)
