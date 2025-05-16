from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import Attribute, Projection, RAQuery, Relation


@pytest.mark.parametrize(
    'ra_ast,expected_sql',
    [
        # Qualified
        (
            Projection(
                attributes=[Attribute(name='dept_name', relation='department')],
                subquery=Relation(name='department'),
            ),
            'SELECT DISTINCT dept_name FROM department',
        ),
        # Unqualified
        (
            Projection(
                attributes=[Attribute(name='dept_name')],
                subquery=Relation(name='department'),
            ),
            'SELECT DISTINCT department.dept_name FROM department',
        ),
        # Multiple attributes
        (
            Projection(
                attributes=[
                    Attribute(name='dept_id'),
                    Attribute(name='dept_name'),
                ],
                subquery=Relation(name='department'),
            ),
            'SELECT DISTINCT dept_id, dept_name FROM department',
        ),
        # Duplicate attributes
        (
            Projection(
                attributes=[
                    Attribute(name='name'),
                    Attribute(name='name'),
                ],
                subquery=Relation(name='employee'),
            ),
            'SELECT DISTINCT name, name FROM employee',
        ),
    ],
)
def test_projection_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
