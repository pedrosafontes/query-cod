from functools import singledispatch

from .. import ast as ra
from ..ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryOperator,
    BooleanExpression,
    BooleanOperation,
    Comparison,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
    JoinKind,
    OuterJoinKind,
    Projection,
    RAQuery,
    Relation,
    Rename,
    Selection,
    SetOperator,
    SetOperatorKind,
    ThetaJoin,
    TopN,
    UnaryOperator,
)
from . import utils as latex
from .utils import multiline, overset, paren, subscript, text


def convert(query: RAQuery, pretty: bool = False) -> str:
    if pretty:
        return multiline(_convert(query, pretty))
    else:
        return _convert(query)


def _convert(query: RAQuery, pretty: bool = False) -> str:
    if isinstance(query, UnaryOperator):
        code = _convert_query(query) + '\n' + _convert_unary_operand(query.operand, pretty)
    elif isinstance(query, BinaryOperator):
        code = (
            _convert_binary_operand(query.left, pretty)
            + '\n'
            + _convert_query(query)
            + '\n'
            + _convert_binary_operand(query.right, pretty)
        )
    else:
        # Relation
        code = _convert_query(query)

    if pretty:
        code = code.replace('\n', '\\\\')

    return code


def _convert_unary_operand(subquery: RAQuery, pretty: bool) -> str:
    latex_query = _convert(subquery, pretty)
    if isinstance(subquery, Relation | UnaryOperator):
        return latex_query
    else:
        return paren(latex_query)


def _convert_binary_operand(subquery: RAQuery, pretty: bool) -> str:
    latex_query = _convert(subquery, pretty)
    if isinstance(subquery, Relation):
        return latex_query
    else:
        return paren(latex_query)


@singledispatch
def _convert_query(query: RAQuery) -> str:
    raise NotImplementedError(f'No LaTeX conversion for {type(query).__name__} implemented.')


@_convert_query.register
def _(rel: Relation) -> str:
    return text(rel.name)


@_convert_query.register
def _(proj: Projection) -> str:
    attributes = [convert_attribute(attr) for attr in proj.attributes]
    return subscript(latex.PI, ', '.join(attributes))


@_convert_query.register
def _(sel: Selection) -> str:
    condition = convert_condition(sel.condition)
    return subscript(latex.SIGMA, condition)


@_convert_query.register
def _(rename: Rename) -> str:
    return subscript(latex.RHO, rename.alias)


@_convert_query.register
def _(set_op: SetOperator) -> str:
    operators: dict[SetOperatorKind, str] = {
        SetOperatorKind.UNION: latex.CUP,
        SetOperatorKind.DIFFERENCE: '-',
        SetOperatorKind.INTERSECT: latex.CAP,
        SetOperatorKind.CARTESIAN: latex.TIMES,
    }
    return operators[set_op.kind]


@_convert_query.register
def _(join: Join) -> str:
    operators: dict[JoinKind, str] = {
        JoinKind.NATURAL: latex.JOIN,
        JoinKind.SEMI: latex.LTIMES,
        JoinKind.ANTI: latex.ANTIJOIN,
    }
    return operators[join.kind]


@_convert_query.register
def _(outer_join: ra.OuterJoin) -> str:
    operators: dict[ra.OuterJoinKind, str] = {
        OuterJoinKind.LEFT: latex.LEFTJOIN,
        OuterJoinKind.RIGHT: latex.RIGHTJOIN,
        OuterJoinKind.OUTER: latex.OUTERJOIN,
    }
    return operators[outer_join.kind]


@_convert_query.register
def _(join: ThetaJoin) -> str:
    condition = convert_condition(join.condition)
    return overset(condition, latex.BOWTIE)


@_convert_query.register
def _(_: Division) -> str:
    return latex.DIV


@_convert_query.register
def _(agg: GroupedAggregation) -> str:
    group_by = ', '.join([convert_attribute(attr) for attr in agg.group_by])
    aggregations = ', '.join(
        [
            paren(
                ', '.join(
                    [
                        convert_attribute(a.input),
                        a.aggregation_function.value.lower(),
                        text(a.output),
                    ]
                )
            )
            for a in agg.aggregations
        ]
    )
    return subscript(latex.GAMMA, f'{paren(group_by)}, {paren(aggregations)}')


@_convert_query.register
def _(top: TopN) -> str:
    attr = convert_attribute(top.attribute)
    return subscript(latex.TOP_N, paren(f'{top.limit}, {attr}'))


def convert_attribute(attr: Attribute) -> str:
    if attr.relation:
        return f'{text(attr.relation)}.{text(attr.name)}'
    else:
        return text(attr.name)


def convert_condition(expr: BooleanExpression, parent_prec: int = 0) -> str:
    latex_expr = _convert_condition(expr)
    if isinstance(expr, BooleanOperation) and expr.precedence < parent_prec:
        return paren(latex_expr)
    else:
        return latex_expr


def _convert_condition(condition: BooleanExpression) -> str:
    match condition:
        case BinaryBooleanExpression():
            bool_exprs = {
                ra.And: latex.AND,
                ra.Or: latex.OR,
            }
            return (
                convert_condition(condition.left, condition.precedence)
                + bool_exprs[type(condition)]
                + convert_condition(condition.right, condition.precedence)
            )
        case ra.Not():
            return latex.NOT + convert_condition(condition.expression, condition.precedence)
        case Comparison() as comp:
            comps = {
                ra.EQ: '=',
                ra.NEQ: latex.NEQ,
                ra.GT: '>',
                ra.LT: '<',
                ra.GTE: latex.GEQ,
                ra.LTE: latex.LEQ,
            }
            return _convert_value(comp.left) + comps[type(comp)] + _convert_value(comp.right)
        case Attribute() as attr:
            return convert_attribute(attr)
        case _:
            return str(condition)


def _convert_value(value: ComparisonValue) -> str:
    match value:
        case Attribute() as attr:
            return convert_attribute(attr)
        case str() as string_value:
            return text(f"'{string_value}'")
        case int() | float() | bool() as number_value:
            return str(number_value)
