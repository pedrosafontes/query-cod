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
            'SELECT DISTINCT * FROM department UNION SELECT DISTINCT * FROM department',
        ),
        # Difference
        (
            Relation('employee').difference('employee'),
            'SELECT DISTINCT * FROM employee EXCEPT SELECT DISTINCT * FROM employee',
        ),
        # Intersect
        (
            Relation('department').intersect('department'),
            'SELECT DISTINCT * FROM department INTERSECT SELECT DISTINCT * FROM department',
        ),
        # Cartesian product
        (
            Relation('department').cartesian('employee'),
            'SELECT DISTINCT * FROM department CROSS JOIN employee',
        ),
        # Chained operations
        (
            Relation('department').difference('department').union('department'),
            'SELECT DISTINCT * FROM department UNION (SELECT DISTINCT * FROM department EXCEPT SELECT DISTINCT * FROM department)',
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
            'SELECT DISTINCT * FROM employee CROSS JOIN department',
        ),
    ],
)
def test_set_operation_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
