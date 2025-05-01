import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    Comparison,
    ComparisonOperator,
    GroupedAggregation,
    Projection,
    RAExpression,
    Relation,
    Selection,
    ThetaJoin,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\pi_{name, title} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} Department)',
            Projection(
                attributes=[Attribute('name'), Attribute('title')],
                expression=ThetaJoin(
                    left=Relation('Employee'),
                    right=Relation('Department'),
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('deptno', relation='Employee'),
                        right=Attribute('deptno', relation='Department'),
                    ),
                ),
            ),
        ),
        (
            '\\Gamma_{((deptno),((salary,avg,\\text{avg_sal})))} (\\pi_{deptno, salary} (\\sigma_{location = \\text{"HQ"}} Employee))',
            GroupedAggregation(
                group_by=[Attribute('deptno')],
                aggregations=[
                    Aggregation(
                        input=Attribute('salary'),
                        aggregation_function=AggregationFunction.AVG,
                        output='avg_sal',
                    )
                ],
                expression=Projection(
                    attributes=[Attribute('deptno'), Attribute('salary')],
                    expression=Selection(
                        condition=Comparison(
                            operator=ComparisonOperator.EQUAL,
                            left=Attribute('location'),
                            right='HQ',
                        ),
                        expression=Relation('Employee'),
                    ),
                ),
            ),
        ),
        (
            '\\pi_{name, \\text{dept_name}} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} (\\sigma_{budget > 100000} Department))',
            Projection(
                attributes=[Attribute('name'), Attribute('dept_name')],
                expression=ThetaJoin(
                    left=Relation('Employee'),
                    right=Selection(
                        condition=Comparison(
                            operator=ComparisonOperator.GREATER_THAN,
                            left=Attribute('budget'),
                            right=100000,
                        ),
                        expression=Relation('Department'),
                    ),
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('deptno', relation='Employee'),
                        right=Attribute('deptno', relation='Department'),
                    ),
                ),
            ),
        ),
    ],
)
def test_valid_complex_queries(query: str, expected: RAExpression) -> None:
    assert parse_ra(query) == expected
