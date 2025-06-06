from collections.abc import Callable

import pytest
from queries.services.ra.ast import RAQuery, Relation


@pytest.mark.parametrize(
    'ra_ast,expected_sql',
    [
        (
            Relation('employee'),
            'SELECT * FROM employee',
        ),
    ],
)
def test_relation_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
