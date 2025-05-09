from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    Comparison,
    ComparisonOperator,
    Join,
    JoinOperator,
    RAQuery,
    Relation,
    ThetaJoin,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Natural join
        (
            Join(
                operator=JoinOperator.NATURAL,
                left=Relation('employee'),
                right=Relation('department'),
            ),
            """SELECT * FROM employee NATURAL JOIN department""",
        ),
        # Semi-join
        (
            Join(
                operator=JoinOperator.SEMI,
                left=Relation('employee'),
                right=Relation('department'),
            ),
            """
            SELECT * FROM employee WHERE EXISTS (
                SELECT * FROM department
                WHERE employee.dept_id = department.dept_id
            )
            """,
        ),
        # Theta join
        (
            ThetaJoin(
                left=Relation('employee'),
                right=Relation('department'),
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute(name='age', relation='employee'),
                    right=30,
                ),
            ),
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.age > 30
            """,
        ),
        # Theta join
        (
            ThetaJoin(
                left=Relation('employee'),
                right=Relation('department'),
                condition=Comparison(
                    operator=ComparisonOperator.EQUAL,
                    left=Attribute(name='dept_id', relation='employee'),
                    right=Attribute(name='dept_id', relation='department'),
                ),
            ),
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.dept_id = department.dept_id
            """,
        ),
        # Nested
        (
            Join(
                operator=JoinOperator.NATURAL,
                left=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('employee'),
                    right=Relation('department'),
                ),
                right=Relation('employee'),
            ),
            """
            SELECT * FROM (
                SELECT * FROM employee NATURAL JOIN department
            ) AS sub NATURAL JOIN employee
            """,
        ),
    ],
)
def test_join_execution(
    ra_ast: RAQuery, expected_sql: str, assert_equivalent: Callable[[RAQuery, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
