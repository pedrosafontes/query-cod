from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    EQ,
    RAQuery,
    Relation,
    attribute,
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
        Relation('R').natural_join('S'),
        Relation('Employee').theta_join(
            'Department',
            EQ(attribute('Employee.department'), attribute('Department.name')),
        ),
    ],
)
def test_valid_join(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            Relation('R').natural_join('X'),
            RelationNotFoundError,
        ),
        (
            Relation('R').theta_join(
                Relation('S'),
                EQ(attribute('A'), attribute('G')),
            ),
            AttributeNotFoundError,
        ),
        (
            Relation('R').theta_join(
                Relation('S'),
                EQ(attribute('B'), attribute('D')),
            ),
            TypeMismatchError,
        ),
        (
            Relation('R').theta_join(
                Relation('T'),
                EQ(attribute('A'), attribute('B')),
            ),
            AmbiguousAttributeReferenceError,
        ),
    ],
)
def test_invalid_join(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)
