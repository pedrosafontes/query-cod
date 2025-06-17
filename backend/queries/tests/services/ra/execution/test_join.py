from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    Aggregation,
    AggregationFunction,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Natural join
        (
            Relation('employee').natural_join('department'),
            """SELECT * FROM employee NATURAL JOIN department""",
        ),
        # Semi-join
        (
            Relation('employee').semi_join('department'),
            """
            SELECT * FROM employee WHERE EXISTS (
                SELECT * FROM department
                WHERE employee.dept_id = department.dept_id
            )
            """,
        ),
        # Theta join
        (
            Relation('employee').theta_join(
                'department', condition=GT(attribute('employee.age'), 30)
            ),
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.age > 30
            """,
        ),
        # Theta join
        (
            Relation('employee').theta_join(
                'department',
                condition=EQ(attribute('employee.dept_id'), attribute('department.dept_id')),
            ),
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.dept_id = department.dept_id
            """,
        ),
        # Nested
        (
            Relation('employee').natural_join('department').natural_join('rotation'),
            """
            SELECT * FROM employee NATURAL JOIN department NATURAL JOIN rotation
            """,
        ),
        # ANTI-JOIN
        (
            Relation('employee').anti_join('department'),
            """
            SELECT * FROM employee WHERE NOT EXISTS (
                SELECT * FROM department
                WHERE employee.dept_id = department.dept_id
            )
            """,
        ),
        # OUTER JOINS - Natural outer joins
        (
            Relation('employee').left_join('department'),
            """SELECT * FROM employee NATURAL LEFT JOIN department""",
        ),
        (
            Relation('employee').right_join('department'),
            """SELECT * FROM employee NATURAL RIGHT JOIN department""",
        ),
        (
            Relation('employee').outer_join('department'),
            """SELECT * FROM employee NATURAL FULL JOIN department""",
        ),
        # OUTER JOINS - Conditional outer joins
        (
            Relation('employee').left_join(
                'department',
                condition=EQ(attribute('employee.dept_id'), attribute('department.dept_id')),
            ),
            """
            SELECT * FROM employee
            LEFT JOIN department ON employee.dept_id = department.dept_id
            """,
        ),
        (
            Relation('employee').right_join(
                'department',
                condition=EQ(attribute('employee.dept_id'), attribute('department.dept_id')),
            ),
            """
            SELECT * FROM employee
            RIGHT JOIN department ON employee.dept_id = department.dept_id
            """,
        ),
        (
            Relation('employee').outer_join(
                'department',
                condition=EQ(attribute('employee.dept_id'), attribute('department.dept_id')),
            ),
            """
            SELECT * FROM employee
            FULL JOIN department ON employee.dept_id = department.dept_id
            """,
        ),
        # JOINS WITH SUBQUERIES - Right side is subquery
        (
            Relation('employee').theta_join(
                Relation('department').project('dept_id', 'dept_name'),
                condition=EQ(attribute('employee.dept_id'), attribute('department.dept_id')),
            ),
            """
            SELECT * FROM employee
            INNER JOIN (SELECT dept_id, dept_name FROM department) AS r
            ON employee.dept_id = r.dept_id
            """,
        ),
        # JOINS WITH RENAMED RELATIONS
        (
            Relation('employee').natural_join(Relation('department').rename('dept')),
            """SELECT * FROM employee NATURAL JOIN department AS dept""",
        ),
        # JOIN WITH HAVING CLAUSE - Should wrap in subquery
        (
            Relation('employee')
            .grouped_aggregation(
                ['dept_id'],
                [Aggregation(attribute('dept_id'), AggregationFunction.COUNT, 'employees')],
            )
            .select(GT(attribute('employees'), 5))
            .natural_join('department'),
            """
            SELECT *
            FROM (
                SELECT dept_id, COUNT(dept_id) AS employees
                FROM employee
                GROUP BY dept_id
            ) AS sub
            NATURAL JOIN department
            WHERE employees > 5
            """,
        ),
        # JOIN WITH ORDER BY - Should wrap in subquery
        (
            Relation('employee').top_n(5, 'name').natural_join('department'),
            """
            SELECT *
            FROM (
                SELECT *
                FROM employee
                ORDER BY name
                DESC LIMIT 5
            ) AS l
            NATURAL JOIN department
            """,
        ),
        # NESTED JOINS WITH MIXED TYPES - employee semi-join department, then theta-join rotation
        (
            Relation('employee')
            .semi_join('department')
            .theta_join(
                'rotation',
                condition=EQ(attribute('employee.id'), attribute('rotation.employee_id')),
            ),
            """
            SELECT * FROM (
                SELECT * FROM employee WHERE EXISTS (
                    SELECT * FROM department
                    WHERE employee.dept_id = department.dept_id
                )
            ) AS l
            INNER JOIN rotation ON l.id = rotation.employee_id
            """,
        ),
    ],
)
def test_join_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
