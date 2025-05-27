from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    Aggregation,
    AggregationFunction,
    And,
    Not,
    Or,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Selection + Join + Projection
        (
            Relation('employee')
            .natural_join('department')
            .select(EQ(attribute('dept_name'), 'Engineering'))
            .project('name'),
            """
            SELECT DISTINCT name
            FROM employee
            NATURAL JOIN department
            WHERE dept_name = 'Engineering'
            """,
        ),
        # Grouped Aggregation + Selection
        (
            Relation('employee')
            .grouped_aggregation(
                ['dept_id'],
                [Aggregation(attribute('age'), AggregationFunction.AVG, 'avg_age')],
            )
            .select(GT(attribute('avg_age'), 30)),
            """
            SELECT dept_id, AVG(age) AS avg_age
            FROM employee
            GROUP BY dept_id
            HAVING avg_age > 30
            """,
        ),
        # TopN + Join
        (
            Relation('employee').natural_join('department').top_n(2, 'age'),
            """
            SELECT DISTINCT *
            FROM employee NATURAL JOIN department
            ORDER BY age DESC
            LIMIT 2
            """,
        ),
        # Nested TopN + Selection + Theta Join
        (
            Relation('employee')
            .theta_join(
                'department',
                condition=EQ(
                    attribute('employee.dept_id'),
                    attribute('department.dept_id'),
                ),
            )
            .select(EQ(attribute('department.dept_name'), 'HR'))
            .top_n(1, 'age'),
            """
            SELECT DISTINCT * FROM employee
            CROSS JOIN department
            ON employee.dept_id = department.dept_id
            WHERE department.dept_name = 'HR'
            ORDER BY age DESC LIMIT 1
            """,
        ),
        # Deeply nested binary expression in Selection
        (
            Relation('employee').select(
                And(
                    Or(
                        EQ(attribute('age'), 25),
                        EQ(attribute('age'), 30),
                    ),
                    Not(
                        EQ(attribute('name'), 'Carol'),
                    ),
                )
            ),
            """
            SELECT DISTINCT * FROM employee
            WHERE (age = 25 OR age = 30)
                  AND NOT name = 'Carol'
            """,
        ),
    ],
)
def test_complex_ra_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
