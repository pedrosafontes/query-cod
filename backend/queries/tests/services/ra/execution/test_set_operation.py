from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Relation,
    SetOperation,
    SetOperator,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Union
        (
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
            'SELECT * FROM department UNION SELECT * FROM department',
        ),
        # Difference
        (
            SetOperation(
                operator=SetOperator.DIFFERENCE,
                left=Relation(name='employee'),
                right=Relation(name='employee'),
            ),
            'SELECT * FROM employee EXCEPT SELECT * FROM employee',
        ),
        # Intersect
        (
            SetOperation(
                operator=SetOperator.INTERSECT,
                left=Relation(name='department'),
                right=Relation(name='department'),
            ),
            'SELECT * FROM department INTERSECT SELECT * FROM department',
        ),
        # Cartesian product
        (
            SetOperation(
                operator=SetOperator.CARTESIAN,
                left=Relation(name='department'),
                right=Relation(name='employee'),
            ),
            'SELECT * FROM department CROSS JOIN employee',
        ),
        # Chained operations
        (
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation(name='department'),
                right=SetOperation(
                    operator=SetOperator.DIFFERENCE,
                    left=Relation(name='department'),
                    right=Relation(name='department'),
                ),
            ),
            'SELECT * FROM department UNION (SELECT * FROM department EXCEPT SELECT * FROM department)',
        ),
        # Union after projection
        (
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
            'SELECT dept_name FROM department UNION SELECT name FROM employee',
        ),
        # Difference on projection
        (
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
            'SELECT dept_name FROM department EXCEPT SELECT name FROM employee',
        ),
        # Cartesian product
        (
            SetOperation(
                operator=SetOperator.CARTESIAN,
                left=Relation(name='employee'),
                right=Relation(name='department'),
            ),
            'SELECT * FROM employee CROSS JOIN department',
        ),
    ],
)
def test_set_operation_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
