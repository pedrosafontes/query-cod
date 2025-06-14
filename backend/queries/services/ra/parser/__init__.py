from pathlib import Path
from typing import cast

from lark import Lark, Tree, UnexpectedInput

from ..ast import RAQuery, Relation
from .errors import (
    InvalidAggregationFunctionError,
    InvalidAggregationInputError,
    InvalidAggregationOutputError,
    InvalidOperatorError,
    InvalidSelectionConditionError,
    InvalidThetaJoinConditionError,
    InvalidTopNLimitError,
    InvalidTopNOrderByError,
    MismatchedParenthesisError,
    MissingCommaError,
    MissingGroupingAggregationsError,
    MissingOperandError,
    MissingProjectionAttributesError,
    MissingRenameAliasError,
    MissingSelectionConditionError,
    MissingThetaJoinConditionError,
    RASyntaxError,
)
from .transformer import RATransformer


grammar_path = Path(__file__).parent / 'grammar.lark'

with grammar_path.open() as f:
    grammar = f.read()

parser = Lark(
    grammar,
    start='query',
    parser='lalr',
    propagate_positions=True,
    cache=True,
    tree_class=Tree[Relation],
)


def parse_ra(ra_text: str) -> RAQuery:
    try:
        parse_tree = cast(Tree[Relation], parser.parse(ra_text))
        return RATransformer().transform(parse_tree)
    except UnexpectedInput as u:
        exception_class = (
            u.match_examples(
                parser.parse,
                EXAMPLE_SYNTAX_ERRORS,
                use_accepts=True,
            )
            or RASyntaxError
        )

        raise exception_class(line=u.line, column=u.column) from u


EXAMPLE_SYNTAX_ERRORS: dict[type[RASyntaxError], list[str]] = {
    MismatchedParenthesisError: [
        '\\pi_{A} (R \\Join S',
        '(R \\cup S',
        'R \\cup S)',
        '((R \\cap S)',
        'R - (S',
    ],
    MissingCommaError: [
        '\\pi_{A B} R',
        '\\Gamma_{(A B), (C, count, D)} R',
        '\\Gamma_{(A,B), (C count D)} R',
        '\\Gamma_{(A,B) (C, count, D)} R',
        '\\operatorname{T}_{(10 A)} R',
    ],
    MissingOperandError: [
        'R \\cup',
        '\\cup S',
        'R -',
        '- S',
        '\\Join S',
        'R \\Join',
        'R \\overline{\\Join}',
        'R \\div',
        '\\ltimes S',
    ],
    InvalidOperatorError: [
        'R && S',
        'R + S',
        'R || S',
        'R * S',
        'R ^^ S',
        'R ! S',
    ],
    MissingProjectionAttributesError: [
        '\\pi_{} R',
        '\\pi R',
    ],
    MissingSelectionConditionError: [
        '\\sigma_{} R',
        '\\sigma R',
    ],
    MissingRenameAliasError: [
        '\\rho_{} R',
        '\\rho R',
    ],
    InvalidSelectionConditionError: [
        '\\sigma_{a >} R',
        '\\sigma_{=} R',
        '\\sigma_{a == b} R',
    ],
    MissingThetaJoinConditionError: [
        'R \\overset{}{\\bowtie} S',
    ],
    InvalidThetaJoinConditionError: [
        'R \\overset{a =} {\\bowtie} S',
        'R \\overset{= b} {\\bowtie} S',
    ],
    MissingGroupingAggregationsError: [
        '\\Gamma R',
        '\\Gamma_{} R',
        '\\Gamma_{(A,B),} R',
        '\\Gamma_{(),()} R',
        '\\Gamma_{(A,B),()} R',
    ],
    InvalidAggregationInputError: [
        '\\Gamma_{(A), ((1, sum, B))} R',
        '\\Gamma_{(A), ((a+b, sum, B))} R',
    ],
    InvalidAggregationFunctionError: [
        '\\Gamma_{(A), ((B, total, C))} R',
        '\\Gamma_{(A), ((B, summation, C))} R',
    ],
    InvalidAggregationOutputError: [
        '\\Gamma_{(A), ((B, sum, 123))} R',
        '\\Gamma_{(A), ((B, avg, a+b))} R',
    ],
    InvalidTopNLimitError: [
        '\\operatorname{T}_{(abc, A)} R',
        '\\operatorname{T}_{(, A)} R',
    ],
    InvalidTopNOrderByError: [
        '\\operatorname{T}_{(10, )} R',
        '\\operatorname{T}_{(10, 123)} R',
    ],
}
