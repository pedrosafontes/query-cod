from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    RAQuery,
    Relation,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Union
        (
            Relation('department').union('department'),
            'SELECT * FROM department UNION SELECT * FROM department',
        ),
        # Difference
        (
            Relation('employee').difference('employee'),
            'SELECT * FROM employee EXCEPT SELECT * FROM employee',
        ),
        # Intersect
        (
            Relation('department').intersect('department'),
            'SELECT * FROM department INTERSECT SELECT * FROM department',
        ),
        # Cartesian product
        (
            Relation('department').cartesian('employee'),
            'SELECT * FROM department CROSS JOIN employee',
        ),
        # Chained operations
        (
            Relation('department').difference('department').union('department'),
            'SELECT * FROM department UNION (SELECT * FROM department EXCEPT SELECT * FROM department)',
        ),
        # Union after projection
        (
            Relation('department').project('dept_name').union(Relation('employee').project('name')),
            'SELECT DISTINCT dept_name FROM department UNION SELECT DISTINCT name FROM employee',
        ),
        # Difference on projection
        # (
        #     Relation('department')
        #     .project('dept_name')
        #     .difference(Relation('employee').project('name')),
        #     'SELECT DISTINCT dept_name FROM department EXCEPT SELECT DISTINCT name FROM employee',
        # ),
        # Cartesian product
        (
            Relation('employee').cartesian('department'),
            'SELECT * FROM employee CROSS JOIN department',
        ),
    ],
)
def test_set_operation_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
