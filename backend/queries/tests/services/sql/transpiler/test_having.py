from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    GT,
    Aggregation,
    AggregationFunction,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT COUNT(id) AS num_employees FROM employee HAVING COUNT(id) > 10',
            Relation('employee')
            .grouped_aggregation(
                group_by=[],
                aggregations=[
                    Aggregation(attribute('id'), AggregationFunction.COUNT, 'num_employees'),
                ],
            )
            .select(
                GT(attribute('num_employees'), 10),
            ),
        ),
        (
            'SELECT dept_id, COUNT(id) AS num_employees FROM employee GROUP BY dept_id HAVING COUNT(id) > 10',
            Relation('employee')
            .grouped_aggregation(
                group_by=[attribute('dept_id')],
                aggregations=[
                    Aggregation(attribute('id'), AggregationFunction.COUNT, 'num_employees'),
                ],
            )
            .select(
                GT(attribute('num_employees'), 10),
            ),
        ),
    ],
)
def test_having_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
