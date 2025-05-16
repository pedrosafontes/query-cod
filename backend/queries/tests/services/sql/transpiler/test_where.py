from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    NotExpression,
    RAQuery,
    Relation,
    Selection,
)


@pytest.mark.parametrize(
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM employee WHERE age > 30',
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute(name='age'),
                    right=30,
                ),
                subquery=Relation(name='employee'),
            ),
        ),
        (
            "SELECT * FROM department WHERE dept_name = 'Engineering'",
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.EQUAL,
                    left=Attribute(name='dept_name'),
                    right='Engineering',
                ),
                subquery=Relation(name='department'),
            ),
        ),
        (
            'SELECT * FROM employee WHERE age >= 30 AND age <= 40',
            Selection(
                condition=BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.AND,
                    left=Comparison(
                        operator=ComparisonOperator.GREATER_THAN_EQUAL,
                        left=Attribute(name='age'),
                        right=30,
                    ),
                    right=Comparison(
                        operator=ComparisonOperator.LESS_THAN_EQUAL,
                        left=Attribute(name='age'),
                        right=40,
                    ),
                ),
                subquery=Relation(name='employee'),
            ),
        ),
        (
            "SELECT * FROM employee WHERE name = 'Alice' OR name = 'Carol'",
            Selection(
                condition=BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.OR,
                    left=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='name'),
                        right='Alice',
                    ),
                    right=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='name'),
                        right='Carol',
                    ),
                ),
                subquery=Relation(name='employee'),
            ),
        ),
        (
            "SELECT DISTINCT * FROM employee WHERE NOT (name = 'Bob')",
            Selection(
                condition=NotExpression(
                    expression=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='name'),
                        right='Bob',
                    )
                ),
                subquery=Relation(name='employee'),
            ),
        ),
        (
            "SELECT DISTINCT * FROM employee WHERE (dept_id = 1 AND age > 30) OR name = 'Bob'",
            Selection(
                condition=BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.OR,
                    left=BinaryBooleanExpression(
                        operator=BinaryBooleanOperator.AND,
                        left=Comparison(
                            operator=ComparisonOperator.EQUAL,
                            left=Attribute(name='dept_id'),
                            right=1,
                        ),
                        right=Comparison(
                            operator=ComparisonOperator.GREATER_THAN,
                            left=Attribute(name='age'),
                            right=30,
                        ),
                    ),
                    right=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='name'),
                        right='Bob',
                    ),
                ),
                subquery=Relation(name='employee'),
            ),
        ),
        (
            'SELECT DISTINCT * FROM employee WHERE senior = TRUE',
            Selection(
                condition=Attribute(name='senior'),
                subquery=Relation(name='employee'),
            ),
        ),
    ],
)
def test_where_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
