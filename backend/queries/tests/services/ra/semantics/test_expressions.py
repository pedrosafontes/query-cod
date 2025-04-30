from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    NotExpression,
    RAExpression,
    Relation,
    Selection,
)
from queries.services.ra.semantics.errors import AttributeNotFoundError, TypeMismatchError


@pytest.mark.parametrize(
    'query',
    [
        Relation('R'),
    ],
)
def test_valid_relation(query: RAExpression, assert_valid: Callable[[RAExpression], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('Z'), 10),
                Relation('R'),
            ),
            AttributeNotFoundError,
        ),
        (
            Selection(Comparison(ComparisonOperator.EQUAL, Attribute('B'), 10), Relation('R')),
            TypeMismatchError,
        ),
        # AND between non-booleans
        (
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Attribute('A'),
                    Attribute('B'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Logical NOT on a VARCHAR: ¬B
        (
            Selection(
                NotExpression(Attribute('B')),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Comparison between TEXT and FLOAT: B < C
        (
            Selection(
                Comparison(
                    ComparisonOperator.LESS_THAN,
                    Attribute('B'),
                    Attribute('C'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Comparison between INTEGER and TEXT: A = B
        (
            Selection(
                Comparison(
                    ComparisonOperator.EQUAL,
                    Attribute('A'),
                    Attribute('B'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
    ],
)
def test_invalid_expression(
    query: RAExpression,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAExpression, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
