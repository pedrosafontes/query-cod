import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Relation,
    SetOperation,
    SetOperator,
)
from queries.services.ra.parser.errors import (
    MissingOperandError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('R \\cup S', SetOperation(SetOperator.UNION, Relation('R'), Relation('S'))),
        ('R - S', SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('S'))),
        ('R \\cap S', SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('S'))),
        ('R \\times S', SetOperation(SetOperator.CARTESIAN, Relation('R'), Relation('S'))),
        (
            'R \\cup (S - T)',
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation('R'),
                right=SetOperation(
                    operator=SetOperator.DIFFERENCE,
                    left=Relation('S'),
                    right=Relation('T'),
                ),
            ),
        ),
        (
            '\\pi_{A} R - \\pi_{A} S',
            SetOperation(
                SetOperator.DIFFERENCE,
                Projection([Attribute('A')], Relation('R')),
                Projection([Attribute('A')], Relation('S')),
            ),
        ),
    ],
)
def test_valid_set_operation(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('R \\cup', MissingOperandError),
        ('\\cup S', MissingOperandError),
        ('R -', MissingOperandError),
        ('- S', MissingOperandError),
        ('\\ltimes S', MissingOperandError),
    ],
)
def test_invalid_set_operation(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
