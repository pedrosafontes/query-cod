import pytest
from queries.services.ra.ast import (
    RAQuery,
    Relation,
)
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    MissingOperandError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('R \\cup S', Relation('R').union('S')),
        ('R - S', Relation('R').difference('S')),
        ('R \\cap S', Relation('R').intersect('S')),
        ('R \\times S', Relation('R').cartesian('S')),
        (
            'R \\cup (S - T)',
            Relation('R').union(Relation('S').difference('T')),
        ),
        (
            '\\pi_{A} R - \\pi_{A} S',
            Relation('R').project('A').difference(Relation('S').project('A')),
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
