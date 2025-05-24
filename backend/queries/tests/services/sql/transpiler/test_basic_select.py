from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import RAQuery, Relation


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        ('SELECT dept_name FROM department', Relation('department').project(['dept_name'])),
        (
            'SELECT department.dept_name FROM department',
            Relation('department').project(['department.dept_name']),
        ),
        (
            'SELECT dept_id, dept_name FROM department',
            Relation('department').project(['dept_id', 'dept_name']),
        ),
        (
            'SELECT * FROM department',
            Relation('department'),
        ),
    ],
)
def test_select_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
