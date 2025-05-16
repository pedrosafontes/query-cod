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
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM employee NATURAL JOIN department',
            Join(
                operator=JoinOperator.NATURAL,
                left=Relation(name='employee'),
                right=Relation(name='department'),
            ),
        ),
        (
            """
            SELECT * FROM employee
            CROSS JOIN department
            WHERE employee.age > 30
            """,
            ThetaJoin(
                left=Relation(name='employee'),
                right=Relation(name='department'),
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute(name='age', relation='employee'),
                    right=30,
                ),
            ),
        ),
        (
            """
            SELECT * FROM (
                SELECT * FROM employee NATURAL JOIN department
            ) AS sub NATURAL JOIN employee
            """,
            Join(
                operator=JoinOperator.NATURAL,
                left=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation(name='employee'),
                    right=Relation(name='department'),
                ),
                right=Relation(name='employee'),
            ),
        ),
    ],
)
def test_join_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
