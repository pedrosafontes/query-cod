from collections.abc import Callable

from ..parser.ast import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    And,
    Attribute,
    BinaryBooleanExpression,
    BinaryOperation,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    Not,
    Or,
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


class RALatexConverter:
    @staticmethod
    def convert(query: RAQuery) -> str:
        method: Callable[[RAQuery], str] = getattr(
            RALatexConverter, f'_convert_{type(query).__name__}'
        )
        if isinstance(query, UnaryOperation):
            return method(query) + RALatexConverter._convert_unary_operand(query.subquery)
        elif isinstance(query, BinaryOperation):
            return (
                RALatexConverter._convert_binary_operand(query.left)
                + method(query)
                + RALatexConverter._convert_binary_operand(query.right)
            )
        else:
            # Relation
            return method(query)

    @staticmethod
    def _convert_unary_operand(subquery: RAQuery) -> str:
        if isinstance(subquery, Relation | UnaryOperation):
            return RALatexConverter.convert(subquery)
        else:
            return paren(RALatexConverter.convert(subquery))

    @staticmethod
    def _convert_binary_operand(subquery: RAQuery) -> str:
        if isinstance(subquery, Relation):
            return RALatexConverter.convert(subquery)
        else:
            return paren(RALatexConverter.convert(subquery))

    @staticmethod
    def _convert_Relation(rel: Relation) -> str:  # noqa: N802
        return text(rel.name)

    @staticmethod
    def _convert_Projection(proj: Projection) -> str:  # noqa: N802
        attributes = [RALatexConverter.convert_attribute(attr) for attr in proj.attributes]
        return subscript(latex.PI, ', '.join(attributes))

    @staticmethod
    def _convert_Selection(sel: Selection) -> str:  # noqa: N802
        condition = RALatexConverter.convert_condition(sel.condition)
        return subscript(latex.SIGMA, condition)

    @staticmethod
    def _convert_Rename(rename: Rename) -> str:  # noqa: N802
        return subscript(latex.RHO, rename.alias)

    @staticmethod
    def _convert_SetOperation(set_op: SetOperation) -> str:  # noqa: N802
        operators: dict[SetOperator, str] = {
            SetOperator.UNION: latex.CUP,
            SetOperator.DIFFERENCE: latex.CAP,
            SetOperator.DIFFERENCE: '-',
            SetOperator.CARTESIAN: latex.TIMES,
        }

        return operators[set_op.operator]

    @staticmethod
    def _convert_Join(join: Join) -> str:  # noqa: N802
        operators: dict[JoinOperator, str] = {
            JoinOperator.NATURAL: latex.JOIN,
            JoinOperator.SEMI: latex.LTIMES,
            JoinOperator.ANTI: latex.ANTIJOIN,
        }

        return operators[join.operator]

    @staticmethod
    def _convert_ThetaJoin(join: ThetaJoin) -> str:  # noqa: N802
        condition = RALatexConverter.convert_condition(join.condition)
        return overset(condition, latex.BOWTIE)

    @staticmethod
    def _convert_Division(div: Division) -> str:  # noqa: N802
        return latex.DIV

    @staticmethod
    def _convert_GroupedAggregation(agg: GroupedAggregation) -> str:  # noqa: N802
        group_by = ', '.join([RALatexConverter.convert_attribute(attr) for attr in agg.group_by])
        aggregations = ', '.join(
            [
                paren(
                    ', '.join(
                        [
                            RALatexConverter.convert_attribute(a.input),
                            a.aggregation_function.value.lower(),
                            text(a.output),
                        ]
                    )
                )
                for a in agg.aggregations
            ]
        )

        return subscript(latex.GAMMA, paren(f'{paren(group_by)}, {paren(aggregations)}'))

    @staticmethod
    def _convert_TopN(top: TopN) -> str:  # noqa: N802
        RALatexConverter.convert_attribute(top.attribute)
        attr = RALatexConverter.convert_attribute(top.attribute)
        return subscript(latex.TOP_N, paren(f'{top.limit}, {attr}'))

    @staticmethod
    def convert_attribute(attr: Attribute) -> str:
        if attr.relation:
            return f'{text(attr.relation)}.{text(attr.name)}'
        else:
            return text(attr.name)

    @staticmethod
    def convert_condition(condition: BooleanExpression) -> str:
        match condition:
            case BinaryBooleanExpression():
                bool_exprs = {
                    And: latex.AND,
                    Or: latex.OR,
                }
                return f'({RALatexConverter.convert_condition(condition.left)} {bool_exprs[type(condition)]} {RALatexConverter.convert_condition(condition.right)})'
            case Not():
                return f'{latex.NOT} ({RALatexConverter.convert_condition(condition.expression)})'
            case Comparison() as comp:
                comps = {
                    EQ: '=',
                    NEQ: latex.NEQ,
                    GT: '>',
                    LT: '<',
                    GTE: latex.GEQ,
                    LTE: latex.LEQ,
                }
                return f'({RALatexConverter._convert_value(comp.left)} {comps[type(comp)]} {RALatexConverter._convert_value(comp.right)})'
            case Attribute() as attr:
                return RALatexConverter.convert_attribute(attr)
            case _:
                return str(condition)

    @staticmethod
    def _convert_value(value: ComparisonValue) -> str:
        match value:
            case Attribute() as attr:
                return RALatexConverter.convert_attribute(attr)
            case str() as string_value:
                return text(f"'{string_value}'")
            case int() | float() | bool() as number_value:
                return str(number_value)
