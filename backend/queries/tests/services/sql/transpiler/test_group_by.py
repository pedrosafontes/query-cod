from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    GroupedAggregation,
    RAQuery,
    Relation,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT COUNT(id) AS num_employees FROM employee',
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(
                        input=Attribute('id'),
                        aggregation_function=AggregationFunction.COUNT,
                        output='num_employees',
                    ),
                ],
                operand=Relation('employee'),
            ),
        ),
        (
            'SELECT dept_id, COUNT(id) AS num_employees FROM employee GROUP BY dept_id',
            GroupedAggregation(
                group_by=[Attribute('dept_id')],
                aggregations=[
                    Aggregation(
                        input=Attribute('id'),
                        aggregation_function=AggregationFunction.COUNT,
                        output='num_employees',
                    ),
                ],
                operand=Relation('employee'),
            ),
        ),
        (
            """
            SELECT dept_id, AVG(age) AS avg_age, MIN(age) AS min_age, MAX(age) AS max_age
            FROM employee GROUP BY dept_id
            """,
            GroupedAggregation(
                group_by=[Attribute('dept_id')],
                aggregations=[
                    Aggregation(Attribute('age'), AggregationFunction.AVG, 'avg_age'),
                    Aggregation(Attribute('age'), AggregationFunction.MIN, 'min_age'),
                    Aggregation(Attribute('age'), AggregationFunction.MAX, 'max_age'),
                ],
                operand=Relation('employee'),
            ),
        ),
        (
            'SELECT AVG(age) AS avg_age FROM employee',
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(
                        input=Attribute('age'),
                        aggregation_function=AggregationFunction.AVG,
                        output='avg_age',
                    ),
                ],
                operand=Relation('employee'),
            ),
        ),
    ],
)
def test_group_by_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
