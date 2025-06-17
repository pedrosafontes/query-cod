from functools import singledispatchmethod
from typing import cast

import queries.services.ra.ast as ra
import sqlglot.expressions as sql
from queries.services.sql.types import aggregate_functions
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

        if self._refers_to(condition, query.expressions):
            query = subquery(query, 'sub').select('*')

        if query.args.get('group'):
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
        match join.kind:
            case ra.JoinKind.SEMI | ra.JoinKind.ANTI:
                left, left_alias = self._transpile_relation(join.left, alias='l')
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
            case ra.JoinKind.NATURAL:
                return self._transpile_natural_join(join.left, join.right)

    @_transpile.register
    def _(self, join: ra.OuterJoin) -> Select:
        if join.condition:
            return self._transpile_conditional_join(
                join.left, join.right, join.condition, join.kind.value
            )
        else:
            return self._transpile_natural_join(join.left, join.right, outer_join_kind=join.kind)

    @_transpile.register
    def _(self, join: ra.ThetaJoin) -> Select:
        return self._transpile_conditional_join(join.left, join.right, join.condition, 'INNER')

    def _transpile_join_left(self, operand: RAQuery) -> tuple[Select, str | None]:
        transpiled = self.transpile(operand)
        if not isinstance(transpiled, Select) or any(
            transpiled.args.get(clause) for clause in ('group', 'having', 'order')
        ):
            subquery_alias = 'l'
            return subquery(transpiled, subquery_alias).select('*'), subquery_alias
        else:
            return transpiled, None

    def _transpile_join_right(self, operand: RAQuery) -> tuple[sql.ExpOrStr, str | None]:
        match operand:
            case Relation():
                return operand.name, None
            case ra.Rename(Relation() as base_relation, alias=alias):
                return base_relation.name, alias
            case ra.Rename():
                return self.transpile(operand), operand.alias
            case _:
                return self.transpile(operand), 'r'

    def _transpile_natural_join(
        self,
        left_operand: RAQuery,
        right_operand: RAQuery,
        outer_join_kind: ra.OuterJoinKind | None = None,
    ) -> Select:
        # Determine the join type
        join_type = 'NATURAL'
        if outer_join_kind:
            join_type += f' {outer_join_kind.value}'

        left, _ = self._transpile_join_left(left_operand)
        right, right_alias = self._transpile_join_right(right_operand)

        return left.join(right, join_type=join_type, join_alias=right_alias)

    def _transpile_conditional_join(
        self,
        left_operand: RAQuery,
        right_operand: RAQuery,
        ra_condition: ra.BooleanExpression,
        join_type: str,
    ) -> Select:
        left, left_alias = self._transpile_join_left(left_operand)
        right, right_alias = self._transpile_join_right(right_operand)

        # rename the condition to use the new aliases
        renamings: dict[str, str] = {}
        if left_alias:
            # Left operand was aliased
            left_schema = self._schema_inferrer.infer(left_operand).schema
            renamings.update({tbl: left_alias for tbl in left_schema.keys() if tbl})
        if right_alias and isinstance(right, SQLQuery):
            # Right operand is aliased
            right_schema = self._schema_inferrer.infer(right_operand).schema
            renamings.update({tbl: right_alias for tbl in right_schema.keys() if tbl})
        ra_condition = RAExpressionRenamer(renamings).rename_condition(ra_condition)

        # Apply the join
        return left.join(
            right,
            join_type=join_type,
            on=self._transpile_condition(ra_condition),
            join_alias=right_alias,
        )

    @_transpile.register
    def _(self, agg: ra.GroupedAggregation) -> Select:
        query = self._transpile_select(agg.operand)

        if (
            query.args.get('group')
            or query.args.get('having')
            or any([expr.find(*aggregate_functions) for expr in query.expressions])
        ):
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
            case ra.Rename(Relation(), alias=existing_alias):
                # relation is a renamed base table
                return select, existing_alias
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
