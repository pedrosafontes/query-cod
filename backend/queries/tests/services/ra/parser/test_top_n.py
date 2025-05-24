import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    EQ,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.parser.errors import (
    InvalidTopNLimitError,
    InvalidTopNOrderByError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\operatorname{T}_{(5,score)} R',
            Relation('R').top_n(5, 'score'),
        ),
        (
            "\\operatorname{T}_{(10,price)} (\\sigma_{category = \\text{'electronics'}} Products)",
            Relation('Products')
            .select(EQ(attribute('category'), 'electronics'))
            .top_n(10, 'price'),
        ),
    ],
)
def test_valid_top_n(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\operatorname{T}_{(abc, A)} R', InvalidTopNLimitError),
        ('\\operatorname{T}_{(, A)} R', InvalidTopNLimitError),
        ('\\operatorname{T}_{(10, )} R', InvalidTopNOrderByError),
        ('\\operatorname{T}_{(10, 123)} R', InvalidTopNOrderByError),
    ],
)
def test_invalid_top_n(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
