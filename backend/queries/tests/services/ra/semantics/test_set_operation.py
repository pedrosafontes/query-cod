from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import RAQuery, Relation, SetOperation, SetOperator
from queries.services.ra.semantics.errors import UnionCompatibilityError


@pytest.mark.parametrize(
    'query',
    [
        SetOperation(SetOperator.CARTESIAN, Relation('R'), Relation('S')),
        SetOperation(SetOperator.UNION, Relation('R'), Relation('U')),
        SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('U')),
        SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('U')),
    ],
)
def test_valid_set_operation(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            SetOperation(SetOperator.UNION, Relation('R'), Relation('T')),
            UnionCompatibilityError,
        ),
        (
            SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('T')),
            UnionCompatibilityError,
        ),
        (
            SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('T')),
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
