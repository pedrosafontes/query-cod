from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    Attribute,
    Projection,
    RAQuery,
    Relation,
    SetOperator,
    SetOperatorKind,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM department UNION SELECT * FROM department',
            SetOperator(
                kind=SetOperatorKind.UNION,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM department EXCEPT SELECT * FROM department',
            SetOperator(
                kind=SetOperatorKind.DIFFERENCE,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM department INTERSECT SELECT * FROM department',
            SetOperator(
                kind=SetOperatorKind.INTERSECT,
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
            SetOperator(
                kind=SetOperatorKind.UNION,
                left=Projection(
                    attributes=[Attribute(name='dept_name')],
                    operand=Relation(name='department'),
                ),
                right=Projection(
                    attributes=[Attribute(name='name')],
                    operand=Relation(name='employee'),
                ),
            ),
        ),
        (
            'SELECT dept_name FROM department EXCEPT SELECT name FROM employee',
            SetOperator(
                kind=SetOperatorKind.DIFFERENCE,
                left=Projection(
                    attributes=[Attribute(name='dept_name')],
                    operand=Relation(name='department'),
                ),
                right=Projection(
                    attributes=[Attribute(name='name')],
                    operand=Relation(name='employee'),
                ),
            ),
        ),
    ],
)
def test_set_operation_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
