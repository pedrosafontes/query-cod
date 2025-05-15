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
                subquery=Relation(name='employee'),
            ),
            'SELECT DISTINCT * FROM employee WHERE age > 30',
        ),
        # Basic string equality
        (
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.EQUAL,
                    left=Attribute(name='dept_name'),
                    right='Engineering',
                ),
                subquery=Relation(name='department'),
            ),
            "SELECT DISTINCT * FROM department WHERE dept_name = 'Engineering'",
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
                subquery=Relation(name='employee'),
            ),
            'SELECT DISTINCT * FROM employee WHERE age >= 30 AND age <= 40',
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
                subquery=Relation(name='employee'),
            ),
            "SELECT DISTINCT * FROM employee WHERE name = 'Alice' OR name = 'Carol'",
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
                subquery=Relation(name='employee'),
            ),
            "SELECT DISTINCT * FROM employee WHERE NOT (name = 'Bob')",
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
                subquery=Relation(name='employee'),
            ),
            "SELECT DISTINCT * FROM employee WHERE (dept_id = 1 AND age > 30) OR name = 'Bob'",
        ),
        # Attribute condition
        (
            Selection(
                condition=Attribute(name='senior'),
                subquery=Relation(name='employee'),
            ),
            'SELECT DISTINCT * FROM employee WHERE senior = TRUE',
        ),
    ],
)
def test_selection_execution(
    ra_ast: RAQuery,
    expected_sql: str,
    assert_equivalent: Callable[[RAQuery, str], None],
) -> None:
    assert_equivalent(ra_ast, expected_sql)
