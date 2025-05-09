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


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Count all employees
        (
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(
                        input=Attribute(name='id'),
                        aggregation_function=AggregationFunction.COUNT,
                        output='num_employees',
                    ),
                ],
                expression=Relation(name='employee'),
            ),
            'SELECT COUNT(id) AS num_employees FROM employee',
        ),
        # Group by dept_id, count per department
        (
            GroupedAggregation(
                group_by=[Attribute(name='dept_id')],
                aggregations=[
                    Aggregation(
                        input=Attribute(name='id'),
                        aggregation_function=AggregationFunction.COUNT,
                        output='num_employees',
                    ),
                ],
                expression=Relation(name='employee'),
            ),
            'SELECT dept_id, COUNT(id) AS num_employees FROM employee GROUP BY dept_id',
        ),
        # Group by dept_id, compute multiple aggregations
        (
            GroupedAggregation(
                group_by=[Attribute(name='dept_id')],
                aggregations=[
                    Aggregation(Attribute('age'), AggregationFunction.AVG, 'avg_age'),
                    Aggregation(Attribute('age'), AggregationFunction.MIN, 'min_age'),
                    Aggregation(Attribute('age'), AggregationFunction.MAX, 'max_age'),
                ],
                expression=Relation(name='employee'),
            ),
            (
                'SELECT dept_id, AVG(age) AS avg_age, MIN(age) AS min_age, MAX(age) AS max_age '
                'FROM employee GROUP BY dept_id'
            ),
        ),
        # Global aggregation with AVG only
        (
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(Attribute('age'), AggregationFunction.AVG, 'avg_age'),
                ],
                expression=Relation(name='employee'),
            ),
            'SELECT AVG(age) AS avg_age FROM employee',
        ),
    ],
)
def test_grouped_aggregation_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
