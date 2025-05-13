from collections.abc import Callable

from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonOperator,
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
from queries.services.types import RelationalSchema
from queries.types import QueryError

from ..semantics import validate_ra_semantics
from .types import RATree
from .utils import (
    CAP,
    CUP,
    DIV,
    GAMMA,
    GEQ,
    JOIN,
    LAND,
    LEQ,
    LNOT,
    LOR,
    LTIMES,
    NEQ,
    PI,
    SIGMA,
    TIMES,
    overset,
    subscript,
    text,
)


class RATreeBuilder:
    _counter: int
    _subqueries: dict[int, RAQuery]

    def __init__(self, schema: RelationalSchema):
        self._schema = schema

    def build(self, query: RAQuery) -> tuple[RATree, dict[int, RAQuery]]:
        self._counter = 0
        self._subqueries = {}
        return self._build(query), self._subqueries

    def _add_subquery(self, subquery: RAQuery) -> tuple[int, list[QueryError]]:
        query_id = self._counter
        errors = validate_ra_semantics(subquery, self._schema)
        self._counter += 1
        self._subqueries[query_id] = subquery
        return query_id, errors

    def _build(self, query: RAQuery) -> RATree:
        method: Callable[[RAQuery], RATree] = getattr(self, f'_convert_{type(query).__name__}')
        return method(query)

    def _convert_Relation(self, rel: Relation) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(rel)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': text(rel.name),
        }

    def _convert_Projection(self, proj: Projection) -> RATree:  # noqa: N802
        attributes = ', '.join([self._convert_attribute(attr) for attr in proj.attributes])
        query_id, errors = self._add_subquery(proj)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': subscript(PI, attributes),
            'sub_trees': [self._build(proj.subquery)],
        }

    def _convert_Selection(self, sel: Selection) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(sel)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': subscript(SIGMA, self._convert_condition(sel.condition)),
            'sub_trees': [self._build(sel.subquery)],
        }

    def _convert_Division(self, div: Division) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(div)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': DIV,
            'sub_trees': [self._build(div.dividend), self._build(div.divisor)],
        }

    def _convert_SetOperation(self, set_op: SetOperation) -> RATree:  # noqa: N802
        match set_op.operator:
            case SetOperator.UNION:
                operator_label = CUP
            case SetOperator.DIFFERENCE:
                operator_label = '-'
            case SetOperator.INTERSECT:
                operator_label = CAP
            case SetOperator.CARTESIAN:
                operator_label = TIMES

        query_id, errors = self._add_subquery(set_op)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': operator_label,
            'sub_trees': [self._build(set_op.left), self._build(set_op.right)],
        }

    def _convert_Join(self, join: Join) -> RATree:  # noqa: N802
        match join.operator:
            case JoinOperator.NATURAL:
                operator_label = JOIN
            case JoinOperator.SEMI:
                operator_label = LTIMES

        query_id, errors = self._add_subquery(join)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': operator_label,
            'sub_trees': [self._build(join.left), self._build(join.right)],
        }

    def _convert_ThetaJoin(self, join: ThetaJoin) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(join)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': overset(self._convert_condition(join.condition), JOIN),
            'sub_trees': [self._build(join.left), self._build(join.right)],
        }

    def _convert_GroupedAggregation(self, agg: GroupedAggregation) -> RATree:  # noqa: N802
        group_by = ', '.join([self._convert_attribute(attr) for attr in agg.group_by])
        aggregations = ', '.join(
            [
                f'({self._convert_attribute(a.input)}, {a.aggregation_function.value.lower()}, {text(a.output)})'
                for a in agg.aggregations
            ]
        )

        query_id, errors = self._add_subquery(agg)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': subscript(GAMMA, f'(({group_by}), ({aggregations}))'),
            'sub_trees': [self._build(agg.subquery)],
        }

    def _convert_TopN(self, top_n: TopN) -> RATree:  # noqa: N802
        attr = self._convert_attribute(top_n.attribute)

        query_id, errors = self._add_subquery(top_n)
        return {
            'id': query_id,
            'validation_errors': errors,
            'label': subscript('T', f'({top_n.limit}, {attr})'),
            'sub_trees': [self._build(top_n.subquery)],
        }

    def _convert_attribute(self, attr: Attribute) -> str:
        return text(str(attr))

    def _convert_condition(self, condition: BooleanExpression) -> str:
        match condition:
            case BinaryBooleanExpression(operator=op):
                match op:
                    case BinaryBooleanOperator.AND:
                        operator_label = LAND
                    case BinaryBooleanOperator.OR:
                        operator_label = LOR
                return f'({self._convert_condition(condition.left)} {operator_label} {self._convert_condition(condition.right)})'
            case NotExpression():
                return f'{LNOT} ({self._convert_condition(condition.expression)})'
            case Comparison(operator=op):
                match op:
                    case ComparisonOperator.EQUAL:
                        operator_label = '='
                    case ComparisonOperator.NOT_EQUAL:
                        operator_label = NEQ
                    case ComparisonOperator.GREATER_THAN:
                        operator_label = '>'
                    case ComparisonOperator.GREATER_THAN_EQUAL:
                        operator_label = GEQ
                    case ComparisonOperator.LESS_THAN:
                        operator_label = '<'
                    case ComparisonOperator.LESS_THAN_EQUAL:
                        operator_label = LEQ
                return f'({self._convert_comparison_value(condition.left)} {operator_label} {self._convert_comparison_value(condition.right)})'
            case Attribute() as attr:
                return self._convert_attribute(attr)
            case _:
                return str(condition)

    def _convert_comparison_value(self, value: ComparisonValue) -> str:
        match value:
            case Attribute() as attr:
                return self._convert_attribute(attr)
            case str() as string_value:
                return text(f"'{string_value}'")
            case int() | float() | bool() as number_value:
                return str(number_value)
