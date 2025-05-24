import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    EQ,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.parser.errors import (
    MissingCommaError,
    MissingProjectionAttributesError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('\\pi_{Sailor.sname} Sailor', Relation('Sailor').project(['Sailor.sname'])),
        (
            '\\pi_{Boat.bid, Sailor.sid, Sailor.sname} (Boat \\Join Sailor)',
            Relation('Boat')
            .natural_join('Sailor')
            .project(['Boat.bid', 'Sailor.sid', 'Sailor.sname']),
        ),
        (
            '\\pi_{a,b,c} R',
            Relation('R').project(['a', 'b', 'c']),
        ),
        (
            "\\pi_{sname} (\\sigma_{color = \\text{'red'}} Boat)",
            Relation('Boat').select(EQ(attribute('color'), 'red')).project(['sname']),
        ),
    ],
)
def test_valid_projection(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\pi_{} R', MissingProjectionAttributesError),
        ('\\pi R', MissingProjectionAttributesError),
        ('\\pi_{A B} R', MissingCommaError),
    ],
)
def test_invalid_projection(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
