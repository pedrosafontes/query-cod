from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    RAQuery,
    Relation,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Employees who have rotated through all departments
        (
            Relation('rotation')
            .project(['employee_id', 'dept_id'])
            .divide(Relation('department').project(['dept_id'])),
            """
            SELECT DISTINCT employee_id
            FROM rotation
            WHERE NOT EXISTS (
                SELECT dept_id FROM department
                EXCEPT
                SELECT dept_id FROM rotation r2
                WHERE r2.employee_id = rotation.employee_id
            )
            """,
        ),
    ],
)
def test_division_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
