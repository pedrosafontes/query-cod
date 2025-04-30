import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    RAExpression,
    Relation,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('Sailor', Relation('Sailor')),
        ('\\text{Student_2023}', Relation('Student_2023')),
    ],
)
def test_valid_relation(query: str, expected: RAExpression) -> None:
    assert parse_ra(query) == expected
