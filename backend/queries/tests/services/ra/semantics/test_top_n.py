from collections.abc import Callable

import pytest
from queries.services.ra.ast import RAQuery, Relation
from queries.services.ra.semantics.errors import AttributeNotFoundError


@pytest.mark.parametrize(
    'query',
    [
        Relation('R').top_n(10, 'A'),
    ],
)
def test_valid_top_n(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (Relation('R').top_n(10, 'Z'), AttributeNotFoundError),
    ],
)
def test_invalid_top_n(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
