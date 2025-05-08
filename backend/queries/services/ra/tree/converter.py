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
    RAExpression,
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


class RATreeConverter:
    def __init__(self) -> None:
        self._counter = 0

    def convert(self, expr: RAExpression) -> RATree:
        next_id = self._counter
        self._counter += 1
        method: Callable[[RAExpression, int], RATree] = getattr(
            self, f'_convert_{type(expr).__name__}'
        )
        return method(expr, next_id)

    def _convert_Relation(self, rel: Relation, node_id: int) -> RATree:  # noqa: N802
        return {
            'id': node_id,
            'label': text(rel.name),
        }

    def _convert_Projection(self, proj: Projection, node_id: int) -> RATree:  # noqa: N802
        attributes = ', '.join([self._convert_attribute(attr) for attr in proj.attributes])
        return {
            'id': node_id,
            'label': subscript(PI, attributes),
            'sub_trees': [self.convert(proj.expression)],
        }

    def _convert_Selection(self, sel: Selection, node_id: int) -> RATree:  # noqa: N802
        return {
            'id': node_id,
            'label': subscript(SIGMA, self._convert_condition(sel.condition)),
            'sub_trees': [self.convert(sel.expression)],
        }

    def _convert_Division(self, div: Division, node_id: int) -> RATree:  # noqa: N802
        return {
            'id': node_id,
            'label': DIV,
            'sub_trees': [self.convert(div.dividend), self.convert(div.divisor)],
        }

    def _convert_SetOperation(self, set_op: SetOperation, node_id: int) -> RATree:  # noqa: N802
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
            'id': node_id,
            'label': operator_label,
            'sub_trees': [self.convert(set_op.left), self.convert(set_op.right)],
        }

    def _convert_Join(self, join: Join, node_id: int) -> RATree:  # noqa: N802
        match join.operator:
            case JoinOperator.NATURAL:
                operator_label = JOIN
            case JoinOperator.SEMI:
                operator_label = LTIMES

        return {
            'id': node_id,
            'label': operator_label,
            'sub_trees': [self.convert(join.left), self.convert(join.right)],
        }

    def _convert_ThetaJoin(self, join: ThetaJoin, node_id: int) -> RATree:  # noqa: N802
        return {
            'id': node_id,
            'label': overset(self._convert_condition(join.condition), JOIN),
            'sub_trees': [self.convert(join.left), self.convert(join.right)],
        }

    def _convert_GroupedAggregation(self, agg: GroupedAggregation, node_id: int) -> RATree:  # noqa: N802
        group_by = ', '.join([self._convert_attribute(attr) for attr in agg.group_by])
        aggregations = ', '.join(
            [
                f'({self._convert_attribute(a.input)}, {a.aggregation_function.value.lower()}, {text(a.output)})'
                for a in agg.aggregations
            ]
        )
        return {
            'id': node_id,
            'label': subscript(GAMMA, f'(({group_by}), ({aggregations}))'),
            'sub_trees': [self.convert(agg.expression)],
        }

    def _convert_TopN(self, top_n: TopN, node_id: int) -> RATree:  # noqa: N802
        attr = self._convert_attribute(top_n.attribute)
        return {
            'id': node_id,
            'label': subscript('T', f'({top_n.limit}, {attr})'),
            'sub_trees': [self.convert(top_n.expression)],
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
