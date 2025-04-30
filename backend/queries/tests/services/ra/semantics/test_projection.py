from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Projection,
    RAExpression,
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
def test_valid_projection(
    query: RAExpression, assert_valid: Callable[[RAExpression], None]
) -> None:
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
    query: RAExpression,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAExpression, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
