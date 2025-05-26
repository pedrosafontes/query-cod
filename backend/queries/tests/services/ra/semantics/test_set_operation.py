from collections.abc import Callable

import pytest
from queries.services.ra.ast import RAQuery, Relation
from queries.services.ra.semantics.errors import UnionCompatibilityError


@pytest.mark.parametrize(
    'query',
    [
        Relation('R').cartesian('S'),
        Relation('R').union('U'),
        Relation('R').intersect('U'),
        Relation('R').difference('U'),
    ],
)
def test_valid_set_operation(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            Relation('R').union('T'),
            UnionCompatibilityError,
        ),
        (
            Relation('R').intersect('T'),
            UnionCompatibilityError,
        ),
        (
            Relation('R').difference('T'),
            UnionCompatibilityError,
        ),
    ],
)
def test_invalid_set_operation(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
