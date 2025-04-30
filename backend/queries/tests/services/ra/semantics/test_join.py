from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Join,
    JoinOperator,
    RAExpression,
    Relation,
    ThetaJoin,
)
from queries.services.ra.semantics.errors import (
    AmbiguousAttributeReferenceError,
    AttributeNotFoundError,
    RelationNotFoundError,
    TypeMismatchError,
)


@pytest.mark.parametrize(
    'query',
    [
        Join(JoinOperator.NATURAL, Relation('R'), Relation('S')),
        ThetaJoin(
            Relation('Employee'),
            Relation('Department'),
            Comparison(
                ComparisonOperator.EQUAL,
                Attribute('department', 'Employee'),
                Attribute('name', 'Department'),
            ),
        ),
    ],
)
def test_valid_join(query: RAExpression, assert_valid: Callable[[RAExpression], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            Join(JoinOperator.NATURAL, Relation('R'), Relation('X')),
            RelationNotFoundError,
        ),
        (
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('A'), Attribute('G')),
            ),
            AttributeNotFoundError,
        ),
        (
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('B'), Attribute('D')),
            ),
            TypeMismatchError,
        ),
        (
            ThetaJoin(
                Relation('R'),
                Relation('T'),
                Comparison(ComparisonOperator.EQUAL, Attribute('A'), Attribute('B')),
            ),
            AmbiguousAttributeReferenceError,
        ),
    ],
)
def test_invalid_join(
    query: RAExpression,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAExpression, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
