from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    GroupedAggregation,
    RAQuery,
    Relation,
)
from queries.services.ra.semantics.errors import (
    AttributeNotFoundError,
    InvalidFunctionArgumentError,
)


@pytest.mark.parametrize(
    'query',
    [
        GroupedAggregation(
            group_by=[Attribute('A')],
            aggregations=[Aggregation(Attribute('B'), AggregationFunction.COUNT, 'X')],
            sub_query=Relation('R'),
        ),
    ],
)
def test_valid_grouped_aggregation(query: RAQuery, assert_valid: Callable[[RAQuery], None]) -> None:
    assert_valid(query)


@pytest.mark.parametrize(
    'query, expected_exception',
    [
        (
            GroupedAggregation(
                [Attribute('Z')],
                [Aggregation(Attribute('A'), AggregationFunction.SUM, 'X')],
                Relation('R'),
            ),
            AttributeNotFoundError,
        ),
        (
            GroupedAggregation(
                [Attribute('A')],
                [Aggregation(Attribute('Z'), AggregationFunction.SUM, 'X')],
                Relation('R'),
            ),
            AttributeNotFoundError,
        ),
        (
            GroupedAggregation(
                group_by=[Attribute('A')],
                aggregations=[
                    Aggregation(
                        input=Attribute('B'),
                        aggregation_function=AggregationFunction.SUM,
                        output='X',
                    )
                ],
                sub_query=Relation('R'),
            ),
            InvalidFunctionArgumentError,
        ),
    ],
)
def test_invalid_grouped_aggregation(
    query: RAQuery,
    expected_exception: type[Exception],
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    assert_invalid(query, expected_exception)


@pytest.mark.parametrize(
    'function',
    [
        AggregationFunction.SUM,
        AggregationFunction.AVG,
    ],
)
def test_aggregation_function_invalid_on_VARCHAR(
    function: AggregationFunction,
    assert_invalid: Callable[[RAQuery, type[Exception]], None],
) -> None:
    query = GroupedAggregation(
        group_by=[Attribute('A')],
        aggregations=[Aggregation(Attribute('B'), function, 'X')],  # B is VARCHAR
        sub_query=Relation('R'),
    )
    assert_invalid(query, InvalidFunctionArgumentError)


@pytest.mark.parametrize(
    'function, attribute_name',
    [
        (AggregationFunction.SUM, 'A'),  # INTEGER
        (AggregationFunction.AVG, 'A'),  # INTEGER
        (AggregationFunction.MIN, 'A'),  # INTEGER
        (AggregationFunction.MAX, 'A'),  # INTEGER
        (AggregationFunction.SUM, 'C'),  # FLOAT
        (AggregationFunction.AVG, 'C'),  # FLOAT
        (AggregationFunction.MIN, 'C'),  # FLOAT
        (AggregationFunction.MAX, 'C'),  # FLOAT
        (AggregationFunction.COUNT, 'A'),  # any type is fine
        (AggregationFunction.COUNT, 'B'),
        (AggregationFunction.COUNT, 'C'),
    ],
)
def test_aggregation_function_valid_on_compatible_types(
    function: AggregationFunction, attribute_name: str, assert_valid: Callable[[RAQuery], None]
) -> None:
    query = GroupedAggregation(
        group_by=[Attribute('B')],
        aggregations=[Aggregation(Attribute(attribute_name), function, 'X')],
        sub_query=Relation('R'),
    )

    assert_valid(query)
