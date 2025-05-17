from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    Comparison,
    ComparisonOperator,
    GroupedAggregation,
    RAQuery,
    Relation,
    Selection,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT COUNT(id) AS num_employees FROM employee HAVING COUNT(id) > 10',
            Selection(
                condition=Comparison(
                    left=Attribute(name='num_employees'),
                    operator=ComparisonOperator.GREATER_THAN,
                    right=10,
                ),
                subquery=GroupedAggregation(
                    group_by=[],
                    aggregations=[
                        Aggregation(
                            input=Attribute(name='id'),
                            aggregation_function=AggregationFunction.COUNT,
                            output='num_employees',
                        ),
                    ],
                    subquery=Relation(name='employee'),
                ),
            ),
        ),
        (
            'SELECT dept_id, COUNT(id) AS num_employees FROM employee GROUP BY dept_id HAVING COUNT(id) > 10',
            Selection(
                condition=Comparison(
                    left=Attribute(name='num_employees'),
                    operator=ComparisonOperator.GREATER_THAN,
                    right=10,
                ),
                subquery=GroupedAggregation(
                    group_by=[Attribute(name='dept_id')],
                    aggregations=[
                        Aggregation(
                            input=Attribute(name='id'),
                            aggregation_function=AggregationFunction.COUNT,
                            output='num_employees',
                        ),
                    ],
                    subquery=Relation(name='employee'),
                ),
            ),
        ),
    ],
)
def test_having_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
