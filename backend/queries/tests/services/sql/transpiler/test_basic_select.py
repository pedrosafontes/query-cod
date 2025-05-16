from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import Attribute, Projection, RAQuery, Relation


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT dept_name FROM department',
            Projection(
                attributes=[Attribute(name='dept_name')], subquery=Relation(name='department')
            ),
        ),
        (
            'SELECT department.dept_name FROM department',
            Projection(
                attributes=[Attribute(name='dept_name', relation='department')],
                subquery=Relation(name='department'),
            ),
        ),
        (
            'SELECT dept_id, dept_name FROM department',
            Projection(
                attributes=[
                    Attribute(name='dept_id'),
                    Attribute(name='dept_name'),
                ],
                subquery=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM department',
            Relation(name='department'),
        ),
    ],
)
def test_select_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
