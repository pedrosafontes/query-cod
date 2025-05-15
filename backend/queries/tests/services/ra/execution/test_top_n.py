from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    RAQuery,
    Relation,
    Selection,
    TopN,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Top 2 oldest employees
        (
            TopN(
                limit=2,
                attribute=Attribute(name='age'),
                subquery=Relation(name='employee'),
            ),
            'SELECT DISTINCT * FROM employee ORDER BY age DESC LIMIT 2',
        ),
        # Top 10 departments by name
        (
            TopN(
                limit=10,
                attribute=Attribute(name='dept_name'),
                subquery=Relation(name='department'),
            ),
            'SELECT DISTINCT * FROM department ORDER BY dept_name DESC LIMIT 10',
        ),
        # 4. Top 2 oldest employees in dept 1
        (
            TopN(
                limit=2,
                attribute=Attribute(name='age'),
                subquery=Selection(
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='dept_id'),
                        right=1,
                    ),
                    subquery=Relation(name='employee'),
                ),
            ),
            'SELECT DISTINCT * FROM (SELECT * FROM employee WHERE dept_id = 1) ORDER BY age DESC LIMIT 2',
        ),
    ],
)
def test_top_n_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
