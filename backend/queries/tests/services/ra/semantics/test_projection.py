from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    GT,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.semantics.errors import (
    AmbiguousAttributeReferenceError,
    AttributeNotFoundError,
)


@pytest.mark.parametrize(
    'query',
    [
        Relation('R').project('A', 'B'),
        Relation('R').select(GT(attribute('C'), 5.0)).project('A', 'B'),
    ],
)
def test_valid_projection(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (Relation('R').project('Z'), AttributeNotFoundError),
        (
            Relation('R').cartesian('T').project('A'),
            AmbiguousAttributeReferenceError,
        ),
    ],
)
def test_invalid_projection(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
