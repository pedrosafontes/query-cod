from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    GT,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM employee NATURAL JOIN department',
            Relation('employee').natural_join('department'),
        ),
        (
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.age > 30
            """,
            Relation('employee').theta_join(
                'department',
                condition=GT(attribute('employee.age'), 30),
            ),
        ),
        (
            """
            SELECT * FROM (
                SELECT * FROM employee NATURAL JOIN department
            ) AS sub NATURAL JOIN employee
            """,
            Relation('employee').natural_join('department').rename('sub').natural_join('employee'),
        ),
    ],
)
def test_join_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
