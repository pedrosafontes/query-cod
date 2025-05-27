from collections.abc import Callable

import pytest
from queries.services.ra.ast import RAQuery, Relation


@pytest.mark.parametrize(
    'ra_ast,expected_sql',
    [
        # Qualified
        (
            Relation('department').project('department.dept_name'),
            'SELECT DISTINCT dept_name FROM department',
        ),
        # Unqualified
        (
            Relation('department').project('dept_name'),
            'SELECT DISTINCT department.dept_name FROM department',
        ),
        # Multiple attributes
        (
            Relation('department').project('dept_id', 'dept_name'),
            'SELECT DISTINCT dept_id, dept_name FROM department',
        ),
        # Duplicate attributes
        (
            Relation('employee').project('name'),
            'SELECT DISTINCT name, name FROM employee',
        ),
    ],
)
def test_projection_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
