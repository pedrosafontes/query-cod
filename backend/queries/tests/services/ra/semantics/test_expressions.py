from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    EQ,
    GT,
    LT,
    And,
    Not,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.semantics.errors import AttributeNotFoundError, TypeMismatchError


@pytest.mark.parametrize(
    'query',
    [
        Relation('R'),
    ],
)
def test_valid_relation(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            Relation('R').select(GT(attribute('Z'), 10)),
            AttributeNotFoundError,
        ),
        (
            Relation('R').select(EQ(attribute('B'), 10)),
            TypeMismatchError,
        ),
        # AND between non-booleans
        (
            Relation('R').select(And(attribute('A'), attribute('B'))),
            TypeMismatchError,
        ),
        # Logical NOT on a VARCHAR: ¬B
        (
            Relation('R').select(Not(attribute('B'))),
            TypeMismatchError,
        ),
        # Comparison between TEXT and FLOAT: B < C
        (
            Relation('R').select(LT(attribute('B'), attribute('C'))),
            TypeMismatchError,
        ),
        # Comparison between INTEGER and TEXT: A = B
        (
            Relation('R').select(EQ(attribute('A'), attribute('B'))),
            TypeMismatchError,
        ),
    ],
)
def test_invalid_expression(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
