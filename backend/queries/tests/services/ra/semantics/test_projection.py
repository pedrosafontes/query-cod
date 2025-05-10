from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Projection,
    RAQuery,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
)
from queries.services.ra.semantics.errors import (
    AmbiguousAttributeReferenceError,
    AttributeNotFoundError,
)


@pytest.mark.parametrize(
    'query',
    [
        Projection([Attribute('A'), Attribute('B')], Relation('R')),
        Projection(
            [Attribute('A'), Attribute('B')],
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('C'), 5.0),
                Relation('R'),
            ),
        ),
    ],
)
def test_valid_projection(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (Projection([Attribute('Z')], Relation('R')), AttributeNotFoundError),
        (
            Projection(
                [Attribute('A')],
                SetOperation(
                    SetOperator.CARTESIAN,
                    Relation('R'),
                    Relation('T'),
                ),
            ),
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
