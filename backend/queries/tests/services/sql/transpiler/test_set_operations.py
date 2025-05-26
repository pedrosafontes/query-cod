from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    Attribute,
    Projection,
    RAQuery,
    Relation,
    SetOperation,
    SetOperator,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM department UNION SELECT * FROM department',
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM department EXCEPT SELECT * FROM department',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM department INTERSECT SELECT * FROM department',
            SetOperation(
                operator=SetOperator.INTERSECT,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
        ),
        # (
        #     'SELECT * FROM department UNION (SELECT * FROM department EXCEPT SELECT * FROM department)',
        #     SetOperation(
        #         operator=SetOperator.UNION,
        #         left=Relation(name='department'),
        #         right=SetOperation(
        #             operator=SetOperator.DIFFERENCE,
        #             left=Relation(name='department'),
        #             right=Relation(name='department'),
        #         ),
        #     ),
        # ),
        (
            'SELECT dept_name FROM department UNION SELECT name FROM employee',
            SetOperation(
                operator=SetOperator.UNION,
                left=Projection(
                    attributes=[Attribute(name='dept_name')],
                    subquery=Relation(name='department'),
                ),
                right=Projection(
                    attributes=[Attribute(name='name')],
                    subquery=Relation(name='employee'),
                ),
            ),
        ),
        (
            'SELECT dept_name FROM department EXCEPT SELECT name FROM employee',
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Projection(
                    attributes=[Attribute(name='dept_name')],
                    subquery=Relation(name='department'),
                ),
                right=Projection(
                    attributes=[Attribute(name='name')],
                    subquery=Relation(name='employee'),
                ),
            ),
        ),
    ],
)
def test_set_operation_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
