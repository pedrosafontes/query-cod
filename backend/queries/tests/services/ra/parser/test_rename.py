import pytest
from queries.services.ra.ast import (
    RAQuery,
    Relation,
)
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    MissingRenameAliasError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('\\rho_{Men}Sailor', Relation('Sailor').rename('Men')),
        ('\\rho_{\\text{Sailor_1}}Sailor', Relation('Sailor').rename('Sailor_1')),
    ],
)
def test_valid_rename(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\rho_{}Sailor', MissingRenameAliasError),
    ],
)
def test_invalid_rename(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
