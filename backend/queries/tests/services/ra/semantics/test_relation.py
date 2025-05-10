from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import RAQuery, Relation
from queries.services.ra.semantics.errors.reference import RelationNotFoundError


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
        (Relation('X'), RelationNotFoundError),
    ],
)
def test_invalid_relation(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
