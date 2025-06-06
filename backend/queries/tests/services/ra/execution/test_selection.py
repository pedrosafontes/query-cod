from collections.abc import Callable

import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    GTE,
    LTE,
    And,
    Not,
    Or,
    RAQuery,
    Relation,
    attribute,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Basic numeric condition
        (
            Relation('employee').select(GT(attribute('age'), 30)),
            'SELECT * FROM employee WHERE age > 30',
        ),
        # Basic string equality
        (
            Relation('department').select(
                EQ(attribute('dept_name'), 'Engineering'),
            ),
            "SELECT * FROM department WHERE dept_name = 'Engineering'",
        ),
        # Logical AND
        (
            Relation('employee').select(
                And(
                    GTE(attribute('age'), 30),
                    LTE(attribute('age'), 40),
                )
            ),
            'SELECT * FROM employee WHERE age >= 30 AND age <= 40',
        ),
        # Logical OR
        (
            Relation('employee').select(
                Or(
                    EQ(attribute('name'), 'Alice'),
                    EQ(attribute('name'), 'Carol'),
                )
            ),
            "SELECT * FROM employee WHERE name = 'Alice' OR name = 'Carol'",
        ),
        # Logical NOT
        (
            Relation('employee').select(Not(EQ(attribute('name'), 'Bob'))),
            "SELECT * FROM employee WHERE NOT (name = 'Bob')",
        ),
        # Grouped (a AND b) OR c
        (
            Relation('employee').select(
                Or(
                    And(
                        EQ(attribute('dept_id'), 1),
                        GT(attribute('age'), 30),
                    ),
                    EQ(attribute('name'), 'Bob'),
                )
            ),
            "SELECT * FROM employee WHERE (dept_id = 1 AND age > 30) OR name = 'Bob'",
        ),
        # Attribute condition
        (
            Relation('employee').select(attribute('senior')),
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
