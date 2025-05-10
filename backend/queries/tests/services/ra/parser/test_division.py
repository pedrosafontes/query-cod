import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Division,
    Projection,
    RAQuery,
    Relation,
)
from queries.services.ra.parser.errors import (
    MissingOperandError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '(\\pi_{x,y} R) \\div (\\pi_{y} S)',
            Division(
                dividend=Projection([Attribute('x'), Attribute('y')], Relation('R')),
                divisor=Projection([Attribute('y')], Relation('S')),
            ),
        ),
        (
            'R \\div S',
            Division(
                dividend=Relation('R'),
                divisor=Relation('S'),
            ),
        ),
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
