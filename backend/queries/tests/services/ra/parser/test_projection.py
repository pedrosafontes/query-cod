import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Join,
    JoinOperator,
    Projection,
    RAQuery,
    Relation,
    Selection,
)
from queries.services.ra.parser.errors import (
    MissingCommaError,
    MissingProjectionAttributesError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\pi_{Sailor.sname} Sailor',
            Projection([Attribute('sname', relation='Sailor')], Relation('Sailor')),
        ),
        (
            '\\pi_{Boat.bid, Sailor.sid, Sailor.sname} (Boat \\Join Sailor)',
            Projection(
                [
                    Attribute('bid', relation='Boat'),
                    Attribute('sid', relation='Sailor'),
                    Attribute('sname', relation='Sailor'),
                ],
                Join(JoinOperator.NATURAL, Relation('Boat'), Relation('Sailor')),
            ),
        ),
        (
            '\\pi_{a,b,c} R',
            Projection([Attribute('a'), Attribute('b'), Attribute('c')], Relation('R')),
        ),
        (
            "\\pi_{sname} (\\sigma_{color = \\text{'red'}} Boat)",
            Projection(
                attributes=[Attribute('sname')],
                subquery=Selection(
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('color'),
                        right='red',
                    ),
                    subquery=Relation('Boat'),
                ),
            ),
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
