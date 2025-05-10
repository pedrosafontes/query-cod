import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    RAQuery,
    Relation,
    Selection,
    TopN,
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
            TopN(limit=5, attribute=Attribute('score'), sub_query=Relation('R')),
        ),
        (
            "\\operatorname{T}_{(10,price)} (\\sigma_{category = \\text{'electronics'}} Products)",
            TopN(
                limit=10,
                attribute=Attribute('price'),
                sub_query=Selection(
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('category'),
                        right='electronics',
                    ),
                    sub_query=Relation('Products'),
                ),
            ),
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
