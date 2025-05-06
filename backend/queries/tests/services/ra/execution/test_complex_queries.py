from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    GroupedAggregation,
    Join,
    JoinOperator,
    NotExpression,
    Projection,
    RAExpression,
    Relation,
    Selection,
    ThetaJoin,
    TopN,
)


@pytest.mark.parametrize(
    'ra_ast, expected_sql',
    [
        # Selection + Join + Projection
        (
            Projection(
                attributes=[Attribute(name='name')],
                expression=Selection(
                    condition=Comparison(
                        ComparisonOperator.EQUAL,
                        Attribute(name='dept_name'),
                        'Engineering',
                    ),
                    expression=Join(
                        operator=JoinOperator.NATURAL,
                        left=Relation('employee'),
                        right=Relation('department'),
                    ),
                ),
            ),
            """
            SELECT name
            FROM employee
            NATURAL JOIN department
            WHERE dept_name = 'Engineering'
            """,
        ),
        # Grouped Aggregation + Selection
        (
            Selection(
                condition=Comparison(
                    ComparisonOperator.GREATER_THAN,
                    Attribute(name='avg_age'),
                    30,
                ),
                expression=GroupedAggregation(
                    group_by=[Attribute('dept_id')],
                    aggregations=[
                        Aggregation(Attribute('age'), AggregationFunction.AVG, 'avg_age'),
                    ],
                    expression=Relation('employee'),
                ),
            ),
            """
            SELECT dept_id, AVG(age) AS avg_age
            FROM employee
            GROUP BY dept_id
            HAVING avg_age > 30
            """,
        ),
        # TopN + Join
        (
            TopN(
                limit=2,
                attribute=Attribute('age'),
                expression=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('employee'),
                    right=Relation('department'),
                ),
            ),
            """
            SELECT * 
            FROM employee NATURAL JOIN department
            ORDER BY age DESC
            LIMIT 2
            """,
        ),
        # Nested TopN + Selection + Theta Join
        (
            TopN(
                limit=1,
                attribute=Attribute(name='age'),
                expression=Selection(
                    condition=Comparison(
                        ComparisonOperator.EQUAL,
                        Attribute(name='dept_name', relation='department'),
                        'HR',
                    ),
                    expression=ThetaJoin(
                        left=Relation('employee'),
                        right=Relation('department'),
                        condition=Comparison(
                            ComparisonOperator.EQUAL,
                            Attribute(name='dept_id', relation='employee'),
                            Attribute(name='dept_id', relation='department'),
                        ),
                    ),
                ),
            ),
            """
            SELECT * FROM employee
            CROSS JOIN department
            ON employee.dept_id = department.dept_id
            WHERE department.dept_name = 'HR'
            ORDER BY age DESC LIMIT 1
            """,
        ),
        # Deeply nested binary expression in Selection
        (
            Selection(
                condition=BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    left=BinaryBooleanExpression(
                        BinaryBooleanOperator.OR,
                        Comparison(
                            ComparisonOperator.EQUAL,
                            Attribute('age'),
                            25,
                        ),
                        Comparison(
                            ComparisonOperator.EQUAL,
                            Attribute('age'),
                            30,
                        ),
                    ),
                    right=NotExpression(
                        Comparison(
                            ComparisonOperator.EQUAL,
                            Attribute('name'),
                            'Carol',
                        )
                    ),
                ),
                expression=Relation('employee'),
            ),
            """
            SELECT * FROM employee
            WHERE (age = 25 OR age = 30) 
                  AND NOT name = 'Carol'
            """,
        ),
    ],
)
def test_complex_ra_execution(
    ra_ast: RAExpression, expected_sql: str, assert_equivalent: Callable[[RAExpression, str], None]
) -> None:
    assert_equivalent(ra_ast, expected_sql)
