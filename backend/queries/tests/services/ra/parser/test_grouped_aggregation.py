import pytest
from queries.services.ra.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    GroupedAggregation,
    RAQuery,
    Relation,
)
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    InvalidAggregationFunctionError,
    InvalidAggregationInputError,
    InvalidAggregationOutputError,
    MissingCommaError,
    MissingGroupingAggregationsError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\Gamma_{((a,b),((c,avg,x)))} R',
            GroupedAggregation(
                group_by=[Attribute('a'), Attribute('b')],
                aggregations=[
                    Aggregation(
                        input=Attribute('c'),
                        aggregation_function=AggregationFunction.AVG,
                        output='x',
                    )
                ],
                operand=Relation('R'),
            ),
        ),
        (
            '\\Gamma_{((deptno),((salary,avg,\\text{avg_sal}),(salary,max,\\text{max_sal}),(salary,min,\\text{min_sal})))} Employee',
            GroupedAggregation(
                group_by=[Attribute('deptno')],
                aggregations=[
                    Aggregation(Attribute('salary'), AggregationFunction.AVG, 'avg_sal'),
                    Aggregation(Attribute('salary'), AggregationFunction.MAX, 'max_sal'),
                    Aggregation(Attribute('salary'), AggregationFunction.MIN, 'min_sal'),
                ],
                operand=Relation('Employee'),
            ),
        ),
        (
            '\\Gamma_{((),((salary,avg,\\text{avg_sal})))} Employee',
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(
                        input=Attribute('salary'),
                        aggregation_function=AggregationFunction.AVG,
                        output='avg_sal',
                    )
                ],
                operand=Relation('Employee'),
            ),
        ),
    ],
)
def test_valid_grouped_aggregations(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'agg_function_str, expected_function',
    [
        ('count', AggregationFunction.COUNT),
        ('sum', AggregationFunction.SUM),
        ('avg', AggregationFunction.AVG),
        ('min', AggregationFunction.MIN),
        ('max', AggregationFunction.MAX),
    ],
)
def test_aggregation_functions(
    agg_function_str: str, expected_function: AggregationFunction
) -> None:
    assert parse_ra(
        '\\Gamma_{((dept),((' + f'in,{agg_function_str},out' + ')))} Employee'
    ) == GroupedAggregation(
        group_by=[Attribute('dept')],
        aggregations=[
            Aggregation(
                input=Attribute('in'),
                aggregation_function=expected_function,
                output='out',
            )
        ],
        operand=Relation('Employee'),
    )


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\Gamma_{(A B), (C, count, D)} R', MissingCommaError),
        ('\\Gamma_{(A,B), (C count D)} R', MissingCommaError),
        ('\\Gamma_{(A,B) (C, count, D)} R', MissingCommaError),
        ('\\Gamma R', MissingGroupingAggregationsError),
        ('\\Gamma_{} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A,B))} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((),())} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A,B),())} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A), ((1, sum, B)))} R', InvalidAggregationInputError),
        ('\\Gamma_{((A), ((a+b, sum, B)))} R', InvalidAggregationInputError),
        ('\\Gamma_{((A), ((B, total, C)))} R', InvalidAggregationFunctionError),
        ('\\Gamma_{((A), ((B, summation, C)))} R', InvalidAggregationFunctionError),
        ('\\Gamma_{((A), ((B, sum, 123)))} R', InvalidAggregationOutputError),
        ('\\Gamma_{((A), ((B, avg, a+b)))} R', InvalidAggregationOutputError),
    ],
)
def test_invalid_grouped_aggregations(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
