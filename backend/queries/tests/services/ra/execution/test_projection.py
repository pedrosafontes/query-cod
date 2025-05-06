from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import Attribute, Projection, RAExpression, Relation


@pytest.mark.parametrize(
    'ra_ast,expected_sql',
    [
        (
            Projection(
                attributes=[Attribute(name='dept_name', relation='department')],
                expression=Relation(name='department'),
            ),
            'SELECT dept_name FROM department',
        ),
        (
            Projection(
                attributes=[Attribute(name='dept_name')],
                expression=Relation(name='department'),
            ),
            'SELECT dept_name FROM department',
        ),
        (
            Projection(
                attributes=[
                    Attribute(name='id'),
                    Attribute(name='dept_name'),
                ],
                expression=Relation(name='department'),
            ),
            'SELECT id, dept_name FROM department',
        ),
        (
            Projection(
                attributes=[
                    Attribute(name='name'),
                    Attribute(name='name'),
                ],
                expression=Relation(name='employee'),
            ),
            'SELECT name, name FROM employee',
        ),
    ],
)
def test_projection_execution(
    ra_ast: RAExpression, expected_sql: str, assert_equivalent: Callable[[RAExpression, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
