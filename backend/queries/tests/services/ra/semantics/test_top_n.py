from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import Attribute, RAQuery, Relation, TopN
from queries.services.ra.semantics.errors import AttributeNotFoundError


@pytest.mark.parametrize(
    'query',
    [
        TopN(10, Attribute('A'), Relation('R')),
    ],
)
def test_valid_top_n(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (TopN(10, Attribute('Z'), Relation('R')), AttributeNotFoundError),
    ],
)
def test_invalid_top_n(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
