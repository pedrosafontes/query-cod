from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
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
            Relation('employee').natural_join('department').natural_join('employee'),
            """
            SELECT * FROM (
                SELECT * FROM employee NATURAL JOIN department
            ) AS sub NATURAL JOIN employee
            """,
        ),
    ],
)
def test_join_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
