from collections.abc import Callable
from typing import cast

from queries.services.sql.semantics.types import aggregate_functions
from queries.services.types import RelationalSchema, SQLQuery
from sqlglot.expressions import (
    EQ,
    Boolean,
    Exists,
    ExpOrStr,
    Expression,
    Select,
    and_,
    column,
    not_,
    or_,
    select,
    subquery,
)

from ..parser.ast import (
    Aggregation,
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    NotExpression,
    Projection,
    RAQuery,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from ..shared.inference import SchemaInferrer
from .renamer import RAExpressionRenamer


class RAtoSQLTranspiler:
    def __init__(self, schema: RelationalSchema, distinct: bool = True):
        self._schema_inferrer = SchemaInferrer(schema)
        self._distinct = distinct

    def transpile(self, query: RAQuery) -> SQLQuery:
        method: Callable[[RAQuery], Select] = getattr(self, f'_transpile_{type(query).__name__}')
        return method(query)

    def _transpile_Relation(self, rel: Relation) -> Select:  # noqa: N802
        return select('*').from_(rel.name).distinct(distinct=self._distinct)

    def _transpile_Projection(self, proj: Projection) -> Select:  # noqa: N802
        query = self._transpile_select(proj.subquery)

        if any(
            [expr.find(*aggregate_functions) for expr in cast(list[Expression], query.expressions)]
        ):
            query = subquery(query, 'sub')

        return query.select(
            *[self._transpile_attribute(attr) for attr in proj.attributes], append=False
        )

    def _transpile_Selection(self, selection: Selection) -> Select:  # noqa: N802
        query = self._transpile_select(selection.subquery)
        condition = self._transpile_condition(selection.condition)
        if query.args.get('group'):
            return query.having(condition)
        else:
            return query.where(condition)

    def _transpile_condition(self, cond: BooleanExpression) -> ExpOrStr:
        match cond:
            case BinaryBooleanExpression():
                left = self._transpile_condition(cond.left)
                right = self._transpile_condition(cond.right)
                match cond.operator:
                    case BinaryBooleanOperator.AND:
                        return and_(left, right)
                    case BinaryBooleanOperator.OR:
                        return or_(left, right)
            case NotExpression():
                return not_(self._transpile_condition(cond.expression))
            case Comparison():
                left = self._transpile_comparison_value(cond.left)
                right = self._transpile_comparison_value(cond.right)
                return f'{left} {cond.operator} {right}'
            case Attribute() as attr:
                return EQ(this=self._transpile_attribute(attr), expression=Boolean(this=True))

    def _transpile_Division(self, div: Division) -> Expression:  # noqa: N802
        # Get tables with aliases
        dividend, dividend_alias = self._transpile_relation(div.dividend, 'dividend')
        dividend_sub, dividend_sub_alias = self._transpile_relation(div.dividend, 'dividend_sub')

        output_attrs = [a.name for a in self._schema_inferrer.infer(div).attrs]
        divisor_attrs = [a.name for a in self._schema_inferrer.infer(div.divisor).attrs]

        # Create join conditions between the two dividend instances
        match_conditions = [
            EQ(
                this=column(attr, table=dividend_sub_alias),
                expression=column(attr, table=dividend_alias),
            )
            for attr in output_attrs
        ]

        # For each dividend tuple:
        # 1. Find all divisor tuples associated with it
        found_divisors = dividend_sub.select(*divisor_attrs, append=False).where(*match_conditions)
        # 2. Check if there are any divisor tuples that are not associated with it
        divisor = self.transpile(div.divisor)
        missing_divisors = divisor.except_(found_divisors)

        candidates = dividend.select(*output_attrs, append=False).distinct()
        return candidates.where(not_(Exists(this=missing_divisors)))

    def _transpile_attribute(self, attr: Attribute) -> Expression:
        return column(attr.name, table=attr.relation)

    def _transpile_comparison_value(self, comparison: ComparisonValue) -> ExpOrStr:
        if isinstance(comparison, Attribute):
            return self._transpile_attribute(comparison)
        elif isinstance(comparison, str):
            return f"'{comparison}'"  # String literal
        else:
            return str(comparison)  # Numbers and other literals

    def _transpile_SetOperation(self, op: SetOperation) -> SQLQuery:  # noqa: N802
        left = self.transpile(op.left)
        right = self.transpile(op.right)

        match op.operator:
            case SetOperator.UNION:
                return left.union(right)
            case SetOperator.INTERSECT:
                return left.intersect(right)
            case SetOperator.DIFFERENCE:
                return left.except_(right)
            case SetOperator.CARTESIAN:
                left = self._transpile_select(op.left)
                if isinstance(op.right, Relation):
                    # op.right is a base table
                    return left.join(op.right.name, join_type='CROSS')
                else:
                    # right is a derived relation
                    return left.join(right, join_type='CROSS', join_alias='r')

    def _transpile_Join(self, join: Join) -> Select:  # noqa: N802
        left, left_alias = self._transpile_relation(join.left, alias='l')

        match join.operator:
            case JoinOperator.NATURAL:
                if isinstance(join.right, Relation):
                    # join.right is a base table
                    return left.join(join.right.name, join_type='NATURAL')
                else:
                    # right is a derived relation
                    right = self.transpile(join.right)
                    return left.join(right, join_type='NATURAL', join_alias='r')

            case JoinOperator.SEMI:
                right, right_alias = self._transpile_relation(join.right, 'r')
                common = self._common_attrs(join.left, join.right)

                return left.where(
                    Exists(
                        this=right.where(
                            *[
                                EQ(
                                    this=column(name, table=left_alias),
                                    expression=column(name, table=right_alias),
                                )
                                for name in common
                            ]
                        )
                    )
                )

    def _transpile_ThetaJoin(self, join: ThetaJoin) -> Select:  # noqa: N802
        left, left_alias = self._transpile_relation(join.left, 'l')

        # rename the attributes in the left relation to use the alias
        left_schema = self._schema_inferrer.infer(join.left).schema
        renamings: dict[str, str] = {}
        for table in left_schema.keys():
            if table:
                renamings[table] = left_alias

        right: ExpOrStr
        if isinstance(join.right, Relation):
            # right is a base table
            right = join.right.name
            right_alias = None
        else:
            # right is a derived relation
            right = self.transpile(join.right)
            right_alias = 'r'

            # rename the attributes in the right relation to use the alias
            right_schema = self._schema_inferrer.infer(join.right).schema
            for table in right_schema.keys():
                if table:
                    renamings[table] = right_alias

        renamed_condition = RAExpressionRenamer(renamings).rename_condition(join.condition)
        condition = self._transpile_condition(renamed_condition)
        return left.join(right, join_alias=right_alias, on=condition)

    def _transpile_GroupedAggregation(self, agg: GroupedAggregation) -> Select:  # noqa: N802
        query = self._transpile_select(agg.subquery)

        if query.args.get('group_by'):
            query = subquery(query, 'sub')

        attrs = [self._transpile_attribute(attr) for attr in agg.group_by]

        return (
            query.select(*attrs, append=False)
            .select(*[self._transpile_aggregation(a) for a in agg.aggregations])
            .group_by(*attrs)
        )

    def _transpile_aggregation(self, agg: Aggregation) -> ExpOrStr:
        return f'{agg.aggregation_function}({agg.input}) AS {agg.output}'

    def _transpile_TopN(self, top_n: TopN) -> Select:  # noqa: N802
        query = self._transpile_select(top_n.subquery)
        return query.limit(top_n.limit).order_by(self._transpile_attribute(top_n.attribute).desc())

    def _transpile_relation(self, relation: RAQuery, alias: str) -> tuple[Select, str]:
        select = self._transpile_select(relation)
        if isinstance(relation, Relation):
            # relation is a base table
            return select, relation.name
        else:
            # relation is a derived relation; therefore, it needs to be aliased
            return subquery(select, alias).select('*').distinct(distinct=self._distinct), alias

    def _transpile_select(self, query: RAQuery) -> Select:
        sql_query = self.transpile(query)
        if not isinstance(sql_query, Select):
            sql_query = subquery(sql_query, 'set_op').select('*')

        return sql_query.distinct(distinct=self._distinct)

    def _common_attrs(self, left: RAQuery, right: RAQuery) -> list[str]:
        l_output = self._schema_inferrer.infer(left)
        r_output = self._schema_inferrer.infer(right)

        l_names = {attr.name for attr in l_output.attrs}
        r_names = {attr.name for attr in r_output.attrs}
        return list(l_names & r_names)
