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
    'ra_ast, expected_sql',
    [
        # Basic numeric condition
        (
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute(name='age'),
                    right=30,
                ),
                sub_query=Relation(name='employee'),
            ),
            'SELECT * FROM employee WHERE age > 30',
        ),
        # Basic string equality
        (
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.EQUAL,
                    left=Attribute(name='dept_name'),
                    right='Engineering',
                ),
                sub_query=Relation(name='department'),
            ),
            "SELECT * FROM department WHERE dept_name = 'Engineering'",
        ),
        # Logical AND
        (
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
                sub_query=Relation(name='employee'),
            ),
            'SELECT * FROM employee WHERE age >= 30 AND age <= 40',
        ),
        # Logical OR
        (
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
                sub_query=Relation(name='employee'),
            ),
            "SELECT * FROM employee WHERE name = 'Alice' OR name = 'Carol'",
        ),
        # Logical NOT
        (
            Selection(
                condition=NotExpression(
                    expression=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute(name='name'),
                        right='Bob',
                    )
                ),
                sub_query=Relation(name='employee'),
            ),
            "SELECT * FROM employee WHERE NOT (name = 'Bob')",
        ),
        # Grouped (a AND b) OR c
        (
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
                sub_query=Relation(name='employee'),
            ),
            "SELECT * FROM employee WHERE (dept_id = 1 AND age > 30) OR name = 'Bob'",
        ),
        # Attribute condition
        (
            Selection(
                condition=Attribute(name='senior'),
                sub_query=Relation(name='employee'),
            ),
            'SELECT * FROM employee WHERE senior = TRUE',
        ),
    ],
)
def test_selection_execution(
    ra_ast: RAQuery,
    expected_sql: str,
    assert_equivalent: Callable[[RAQuery, str], None],
) -> None:
    assert_equivalent(ra_ast, expected_sql)
