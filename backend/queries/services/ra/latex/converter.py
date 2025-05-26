
from functools import singledispatch

from ..parser import ast as ra
from ..parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryOperation,
    BooleanExpression,
    BooleanOperation,
    Comparison,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    Projection,
    RAQuery,
    Relation,
    Rename,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
    UnaryOperation,
)
from . import utils as latex
from .utils import overset, paren, subscript, text


def convert(query: RAQuery) -> str:
    if isinstance(query, UnaryOperation):
        return _convert_query(query) + '\n' + _convert_unary_operand(query.subquery)
    elif isinstance(query, BinaryOperation):
        return (
            _convert_binary_operand(query.left)
            + '\n'
            + _convert_query(query)
            + '\n'
            + _convert_binary_operand(query.right)
        )
    else:
        # Relation
        return _convert_query(query)


def _convert_unary_operand(subquery: RAQuery) -> str:
    latex_query = convert(subquery)
    if isinstance(subquery, Relation | UnaryOperation):
        return latex_query
    else:
        return paren(latex_query)


def _convert_binary_operand(subquery: RAQuery) -> str:
    latex_query = convert(subquery)
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
def _(set_op: SetOperation) -> str:
    operators: dict[SetOperator, str] = {
        SetOperator.UNION: latex.CUP,
        SetOperator.DIFFERENCE: latex.CAP,
        SetOperator.DIFFERENCE: '-',
        SetOperator.CARTESIAN: latex.TIMES,
    }
    return operators[set_op.operator]


@_convert_query.register
def _(join: Join) -> str:
    operators: dict[JoinOperator, str] = {
        JoinOperator.NATURAL: latex.JOIN,
        JoinOperator.SEMI: latex.LTIMES,
        JoinOperator.ANTI: latex.ANTIJOIN,
    }
    return operators[join.operator]


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
    return subscript(latex.GAMMA, paren(f'{paren(group_by)}, {paren(aggregations)}'))


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
                + '\n'
                + bool_exprs[type(condition)]
                + '\n'
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
