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
        (
            '(\\pi_{x,y} R) \\div (\\pi_{y} S)',
            Relation('R').project('x', 'y').divide(Relation('S').project('y')),
        ),
        ('R \\div S', Relation('R').divide('S')),
    ],
)
def test_valid_division(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('R \\div', MissingOperandError),
    ],
)
def test_invalid_division(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
