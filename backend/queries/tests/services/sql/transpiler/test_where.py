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
    'sql_text,expected_ra',
    [
        (
            'SELECT * FROM employee WHERE age > 30',
            Relation('employee').select(GT(attribute('age'), 30)),
        ),
        (
            "SELECT * FROM department WHERE dept_name = 'Engineering'",
            Relation('department').select(EQ(attribute('dept_name'), 'Engineering')),
        ),
        (
            'SELECT * FROM employee WHERE age >= 30 AND age <= 40',
            Relation('employee').select(
                And(
                    GTE(attribute('age'), 30),
                    LTE(attribute('age'), 40),
                )
            ),
        ),
        (
            "SELECT * FROM employee WHERE name = 'Alice' OR name = 'Carol'",
            Relation('employee').select(
                Or(
                    EQ(attribute('name'), 'Alice'),
                    EQ(attribute('name'), 'Carol'),
                )
            ),
        ),
        (
            "SELECT DISTINCT * FROM employee WHERE NOT (name = 'Bob')",
            Relation('employee').select(
                Not(EQ(attribute('name'), 'Bob')),
            ),
        ),
        (
            "SELECT DISTINCT * FROM employee WHERE (dept_id = 1 AND age > 30) OR name = 'Bob'",
            Relation('employee').select(
                Or(
                    And(
                        EQ(attribute('dept_id'), 1),
                        GT(attribute('age'), 30),
                    ),
                    EQ(attribute('name'), 'Bob'),
                )
            ),
        ),
        (
            'SELECT DISTINCT * FROM employee WHERE senior = TRUE',
            Relation('employee').select(attribute('senior')),
        ),
    ],
)
def test_where_transpilation(
    sql_text: str, expected_ra: RAQuery, assert_equivalent: Callable[[str, RAQuery], None]
) -> None:
    assert_equivalent(sql_text, expected_ra)
