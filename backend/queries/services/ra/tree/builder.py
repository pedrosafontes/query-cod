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

    def build(self, query: RAQuery) -> tuple[RATree, dict[int, RAQuery]]:
        self._counter = 0
        self._subqueries = {}
        return self._build(query), self._subqueries

    def _add_subquery(self, subquery: RAQuery) -> int:
        subquery_id = self._counter
        self._counter += 1
        self._subqueries[subquery_id] = subquery
        return subquery_id

    def _build(self, query: RAQuery) -> RATree:
        method: Callable[[RAQuery], RATree] = getattr(self, f'_convert_{type(query).__name__}')
        return method(query)

    def _convert_Relation(self, rel: Relation) -> RATree:  # noqa: N802
        return {
            'id': self._add_subquery(rel),
            'label': text(rel.name),
        }

    def _convert_Projection(self, proj: Projection) -> RATree:  # noqa: N802
        attributes = ', '.join([self._convert_attribute(attr) for attr in proj.attributes])
        return {
            'id': self._add_subquery(proj),
            'label': subscript(PI, attributes),
            'sub_trees': [self._build(proj.subquery)],
        }

    def _convert_Selection(self, sel: Selection) -> RATree:  # noqa: N802
        return {
            'id': self._add_subquery(sel),
            'label': subscript(SIGMA, self._convert_condition(sel.condition)),
            'sub_trees': [self._build(sel.subquery)],
        }

    def _convert_Division(self, div: Division) -> RATree:  # noqa: N802
        return {
            'id': self._add_subquery(div),
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

        return {
            'id': self._add_subquery(set_op),
            'label': operator_label,
            'sub_trees': [self._build(set_op.left), self._build(set_op.right)],
        }

    def _convert_Join(self, join: Join) -> RATree:  # noqa: N802
        match join.operator:
            case JoinOperator.NATURAL:
                operator_label = JOIN
            case JoinOperator.SEMI:
                operator_label = LTIMES

        return {
            'id': self._add_subquery(join),
            'label': operator_label,
            'sub_trees': [self._build(join.left), self._build(join.right)],
        }

    def _convert_ThetaJoin(self, join: ThetaJoin) -> RATree:  # noqa: N802
        return {
            'id': self._add_subquery(join),
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
        return {
            'id': self._add_subquery(agg),
            'label': subscript(GAMMA, f'(({group_by}), ({aggregations}))'),
            'sub_trees': [self._build(agg.subquery)],
        }

    def _convert_TopN(self, top_n: TopN) -> RATree:  # noqa: N802
        attr = self._convert_attribute(top_n.attribute)
        return {
            'id': self._add_subquery(top_n),
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
