from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import RAExpression, Relation
from queries.services.ra.semantics.errors.reference import RelationNotFoundError


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
        (Relation('X'), RelationNotFoundError),
    ],
)
def test_invalid_relation(
    query: RAExpression,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAExpression, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
