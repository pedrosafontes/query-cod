import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    Aggregation,
    AggregationFunction,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.parser import parse_ra


@pytest.mark.parametrize(
    'query, expected',
    [
        (
            '\\pi_{name, title} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} Department)',
            Relation('Employee')
            .theta_join(
                'Department', EQ(attribute('Employee.deptno'), attribute('Department.deptno'))
            )
            .project('name', 'title'),
        ),
        (
            "\\Gamma_{(deptno),((salary,avg,\\text{avg_sal}))} (\\pi_{deptno, salary} (\\sigma_{location = \\text{'HQ'}} Employee))",
            Relation('Employee')
            .select(EQ(attribute('location'), 'HQ'))
            .project('deptno', 'salary')
            .grouped_aggregation(
                ['deptno'],
                [
                    Aggregation(
                        input=attribute('salary'),
                        aggregation_function=AggregationFunction.AVG,
                        output='avg_sal',
                    )
                ],
            ),
        ),
        (
            '\\pi_{name, \\text{dept_name}} (Employee \\overset{Employee.deptno = Department.deptno}{\\bowtie} (\\sigma_{budget > 100000} Department))',
            Relation('Employee')
            .theta_join(
                Relation('Department').select(GT(attribute('budget'), 100000)),
                EQ(attribute('Employee.deptno'), attribute('Department.deptno')),
            )
            .project('name', 'dept_name'),
        ),
    ],
)
def test_valid_complex_queries(query: str, expected: RAQuery) -> None:
    assert parse_ra(query) == expected
