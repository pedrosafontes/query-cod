from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    EQ,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Top 2 oldest employees
        (
            Relation('employee').top_n(2, 'age'),
            'SELECT DISTINCT * FROM employee ORDER BY age DESC LIMIT 2',
        ),
        # Top 10 departments by name
        (
            Relation('department').top_n(10, 'dept_name'),
            'SELECT DISTINCT * FROM department ORDER BY dept_name DESC LIMIT 10',
        ),
        # Top 2 oldest employees in dept 1
        (
            Relation('employee').select(EQ(attribute('dept_id'), 1)).top_n(2, 'age'),
            'SELECT DISTINCT * FROM (SELECT * FROM employee WHERE dept_id = 1) ORDER BY age DESC LIMIT 2',
        ),
    ],
)
def test_top_n_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
