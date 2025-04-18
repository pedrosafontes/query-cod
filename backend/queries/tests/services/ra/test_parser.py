import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    NotExpression,
    Projection,
    RAExpression,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from queries.services.ra.parser.errors import (
    InvalidAggregationFunctionError,
    InvalidAggregationInputError,
    InvalidAggregationOutputError,
    InvalidOperatorError,
    InvalidSelectionConditionError,
    InvalidThetaJoinConditionError,
    InvalidTopNLimitError,
    InvalidTopNOrderByError,
    MismatchedParenthesisError,
    MissingCommaError,
    MissingGroupingAggregationsError,
    MissingOperandError,
    MissingProjectionAttributesError,
    MissingSelectionConditionError,
    MissingThetaJoinConditionError,
)


@pytest.mark.parametrize(
    'query, expected',
    [
        ('Sailor', Relation('Sailor')),
        ('\\text{Student_2023}', Relation('Student_2023')),
        (
            '\\pi_{Sailor.sname} Sailor',
            Projection([Attribute('sname', relation='Sailor')], Relation('Sailor')),
        ),
        (
            '\\pi_{Boat.bid, Sailor.sid, Sailor.sname} (Boat \\Join Sailor)',
            Projection(
                [
                    Attribute('bid', relation='Boat'),
                    Attribute('sid', relation='Sailor'),
                    Attribute('sname', relation='Sailor'),
                ],
                Join(JoinOperator.NATURAL, Relation('Boat'), Relation('Sailor')),
            ),
        ),
        (
            '\\pi_{a,b,c} R',
            Projection([Attribute('a'), Attribute('b'), Attribute('c')], Relation('R')),
        ),
        (
            '\\sigma_{a = 5} R',
            Selection(Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5), Relation('R')),
        ),
        (
            '\\sigma_{salary > 50000} Employee',
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('salary'), 50000),
                Relation('Employee'),
            ),
        ),
        (
            '\\sigma_{name = "John"} Employee',
            Selection(
                Comparison(ComparisonOperator.EQUAL, Attribute('name'), 'John'),
                Relation('Employee'),
            ),
        ),
        (
            '\\sigma_{Employee.salary > Department.budget} (Employee \\Join Department)',
            Selection(
                Comparison(
                    ComparisonOperator.GREATER_THAN,
                    Attribute('salary', relation='Employee'),
                    Attribute('budget', relation='Department'),
                ),
                Join(JoinOperator.NATURAL, Relation('Employee'), Relation('Department')),
            ),
        ),
        (
            '\\sigma_{a = 5 \\land b = 10} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                    Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{a = 5 \\lor b = 10} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                    Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5)} R',
            Selection(
                NotExpression(Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5)),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{(a = 5 \\land b > 10) \\lor c = "test"} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    BinaryBooleanExpression(
                        BinaryBooleanOperator.AND,
                        Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                        Comparison(ComparisonOperator.GREATER_THAN, Attribute('b'), 10),
                    ),
                    Comparison(ComparisonOperator.EQUAL, Attribute('c'), 'test'),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{\\lnot (a = 5 \\lor b = 10) \\land c > 20} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    NotExpression(
                        BinaryBooleanExpression(
                            BinaryBooleanOperator.OR,
                            Comparison(ComparisonOperator.EQUAL, Attribute('a'), 5),
                            Comparison(ComparisonOperator.EQUAL, Attribute('b'), 10),
                        )
                    ),
                    Comparison(ComparisonOperator.GREATER_THAN, Attribute('c'), 20),
                ),
                Relation('R'),
            ),
        ),
        (
            '\\sigma_{a = 1 \\lor b = 2 \\land c = 3} R',
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.OR,
                    Comparison(ComparisonOperator.EQUAL, Attribute('a'), 1),
                    BinaryBooleanExpression(
                        BinaryBooleanOperator.AND,
                        Comparison(ComparisonOperator.EQUAL, Attribute('b'), 2),
                        Comparison(ComparisonOperator.EQUAL, Attribute('c'), 3),
                    ),
                ),
                Relation('R'),
            ),
        ),
        ('R \\cup S', SetOperation(SetOperator.UNION, Relation('R'), Relation('S'))),
        ('R - S', SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('S'))),
        ('R \\cap S', SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('S'))),
        ('R \\times S', SetOperation(SetOperator.CARTESIAN, Relation('R'), Relation('S'))),
        ('R \\Join S', Join(JoinOperator.NATURAL, Relation('R'), Relation('S'))),
        ('R \\ltimes S', Join(JoinOperator.SEMI, Relation('R'), Relation('S'))),
        (
            'R \\overset{a = b}{\\bowtie} S',
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('a'), Attribute('b')),
            ),
        ),
        (
            'R \\overset{a > b \\land c = d}{\\bowtie} S',
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Comparison(ComparisonOperator.GREATER_THAN, Attribute('a'), Attribute('b')),
                    Comparison(ComparisonOperator.EQUAL, Attribute('c'), Attribute('d')),
                ),
            ),
        ),
        (
            '(\\pi_{x,y} R) \\div (\\pi_{y} S)',
            Division(
                dividend=Projection([Attribute('x'), Attribute('y')], Relation('R')),
                divisor=Projection([Attribute('y')], Relation('S')),
            ),
        ),
        (
            'R \\cup (S - T)',
            SetOperation(
                operator=SetOperator.UNION,
                left=Relation('R'),
                right=SetOperation(
                    operator=SetOperator.DIFFERENCE,
                    left=Relation('S'),
                    right=Relation('T'),
                ),
            ),
        ),
        (
            'R \\Join (S \\Join T)',
            Join(
                operator=JoinOperator.NATURAL,
                left=Relation('R'),
                right=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('S'),
                    right=Relation('T'),
                ),
            ),
        ),
        (
            'R \\Join S \\Join T',
            Join(
                operator=JoinOperator.NATURAL,
                left=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('R'),
                    right=Relation('S'),
                ),
                right=Relation('T'),
            ),  # assumes left-associative
        ),
        (
            'R \\div S',
            Division(
                dividend=Relation('R'),
                divisor=Relation('S'),
            ),
        ),
        (
            '\\Gamma_{((a,b),((c,avg,x)))} R',
            GroupedAggregation(
                group_by=[Attribute('a'), Attribute('b')],
                aggregations=[
                    Aggregation(
                        input=Attribute('c'),
                        aggregation_function=AggregationFunction.AVG,
                        output='x',
                    )
                ],
                expression=Relation('R'),
            ),
        ),
        (
            '\\Gamma_{((deptno),((salary,avg,\\text{avg_sal}),(salary,max,\\text{max_sal}),(salary,min,\\text{min_sal})))} Employee',
            GroupedAggregation(
                group_by=[Attribute('deptno')],
                aggregations=[
                    Aggregation(Attribute('salary'), AggregationFunction.AVG, 'avg_sal'),
                    Aggregation(Attribute('salary'), AggregationFunction.MAX, 'max_sal'),
                    Aggregation(Attribute('salary'), AggregationFunction.MIN, 'min_sal'),
                ],
                expression=Relation('Employee'),
            ),
        ),
        (
            '\\Gamma_{((),((salary,avg,\\text{avg_sal})))} Employee',
            GroupedAggregation(
                group_by=[],
                aggregations=[
                    Aggregation(
                        input=Attribute('salary'),
                        aggregation_function=AggregationFunction.AVG,
                        output='avg_sal',
                    )
                ],
                expression=Relation('Employee'),
            ),
        ),
        (
            '\\operatorname{T}_{(5,score)} R',
            TopN(limit=5, attribute=Attribute('score'), expression=Relation('R')),
        ),
        (
            '\\operatorname{T}_{(10,price)} (\\sigma_{category = "electronics"} Products)',
            TopN(
                limit=10,
                attribute=Attribute('price'),
                expression=Selection(
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('category'),
                        right='electronics',
                    ),
                    expression=Relation('Products'),
                ),
            ),
        ),
        (
            '\\pi_{sname} (\\sigma_{color = "red"} Boat)',
            Projection(
                attributes=[Attribute('sname')],
                expression=Selection(
                    condition=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('color'),
                        right='red',
                    ),
                    expression=Relation('Boat'),
                ),
            ),
        ),
        (
            '\\sigma_{Sailor.rating > 7} (Sailor \\Join Boat)',
            Selection(
                condition=Comparison(
                    operator=ComparisonOperator.GREATER_THAN,
                    left=Attribute('rating', relation='Sailor'),
                    right=7,
                ),
                expression=Join(
                    operator=JoinOperator.NATURAL,
                    left=Relation('Sailor'),
                    right=Relation('Boat'),
                ),
            ),
        ),
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
            '\\Gamma_{((deptno),((salary,avg,\\text{avg_sal})))} (\\pi_{deptno, salary} (\\sigma_{location = "HQ"} Employee))',
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
def test_parser_ast_equivalence(query: str, expected: RAExpression) -> None:
    assert parse_ra(query) == expected


@pytest.mark.parametrize(
    'op_str, expected_op',
    [
        ('=', ComparisonOperator.EQUAL),
        ('\\neq', ComparisonOperator.NOT_EQUAL),
        ('<', ComparisonOperator.LESS_THAN),
        ('\\lt', ComparisonOperator.LESS_THAN),
        ('\\leq', ComparisonOperator.LESS_THAN_EQUAL),
        ('>', ComparisonOperator.GREATER_THAN),
        ('\\gt', ComparisonOperator.GREATER_THAN),
        ('\\geq', ComparisonOperator.GREATER_THAN_EQUAL),
    ],
)
def test_comparison_operators(op_str: str, expected_op: ComparisonOperator) -> None:
    # Use selection as a wrapper to test comparison expressions
    assert parse_ra(f'\\sigma_{{a {op_str} 5}} R') == Selection(
        condition=Comparison(expected_op, Attribute('a'), 5),
        expression=Relation('R'),
    )


@pytest.mark.parametrize(
    'agg_function_str, expected_function',
    [
        ('count', AggregationFunction.COUNT),
        ('sum', AggregationFunction.SUM),
        ('avg', AggregationFunction.AVG),
        ('min', AggregationFunction.MIN),
        ('max', AggregationFunction.MAX),
    ],
)
def test_aggregation_functions(
    agg_function_str: str, expected_function: AggregationFunction
) -> None:
    assert parse_ra(
        '\\Gamma_{((dept),((' + f'in,{agg_function_str},out' + ')))} Employee'
    ) == GroupedAggregation(
        group_by=[Attribute('dept')],
        aggregations=[
            Aggregation(
                input=Attribute('in'),
                aggregation_function=expected_function,
                output='out',
            )
        ],
        expression=Relation('Employee'),
    )


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('\\pi_{} R', MissingProjectionAttributesError),
        ('\\pi R', MissingProjectionAttributesError),
        ('\\sigma_{} R', MissingSelectionConditionError),
        ('\\sigma R', MissingSelectionConditionError),
        ('\\sigma_{a >} R', InvalidSelectionConditionError),
        ('\\sigma_{=} R', InvalidSelectionConditionError),
        ('\\sigma_{a == b} R', InvalidSelectionConditionError),
        ('R \\overset{}{\\bowtie} S', MissingThetaJoinConditionError),
        ('R \\overset{a =}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('R \\overset{= b}{\\bowtie} S', InvalidThetaJoinConditionError),
        ('\\pi_{A B} R', MissingCommaError),
        ('\\Gamma_{(A B), (C, count, D)} R', MissingCommaError),
        ('\\Gamma_{(A,B), (C count D)} R', MissingCommaError),
        ('\\Gamma_{(A,B) (C, count, D)} R', MissingCommaError),
        ('\\operatorname{T}_{(10 A)} R', MissingCommaError),
        ('R \\cup', MissingOperandError),
        ('\\cup S', MissingOperandError),
        ('R -', MissingOperandError),
        ('- S', MissingOperandError),
        ('\\Join S', MissingOperandError),
        ('R \\div', MissingOperandError),
        ('\\ltimes S', MissingOperandError),
        ('R && S', InvalidOperatorError),
        ('R + S', InvalidOperatorError),
        ('R || S', InvalidOperatorError),
        ('R * S', InvalidOperatorError),
        ('R ^^ S', InvalidOperatorError),
        ('R ! S', InvalidOperatorError),
        ('\\pi_{A} (R \\Join S', MismatchedParenthesisError),
        ('(R \\cup S', MismatchedParenthesisError),
        ('R \\cup S)', MismatchedParenthesisError),
        ('((R \\cap S)', MismatchedParenthesisError),
        ('R - (S', MismatchedParenthesisError),
        ('\\Gamma R', MissingGroupingAggregationsError),
        ('\\Gamma_{} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A,B))} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((),())} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A,B),())} R', MissingGroupingAggregationsError),
        ('\\Gamma_{((A), ((1, sum, B)))} R', InvalidAggregationInputError),
        ('\\Gamma_{((A), ((a+b, sum, B)))} R', InvalidAggregationInputError),
        ('\\Gamma_{((A), ((B, total, C)))} R', InvalidAggregationFunctionError),
        ('\\Gamma_{((A), ((B, summation, C)))} R', InvalidAggregationFunctionError),
        ('\\Gamma_{((A), ((B, sum, 123)))} R', InvalidAggregationOutputError),
        ('\\Gamma_{((A), ((B, avg, a+b)))} R', InvalidAggregationOutputError),
        ('\\operatorname{T}_{(abc, A)} R', InvalidTopNLimitError),
        ('\\operatorname{T}_{(, A)} R', InvalidTopNLimitError),
        ('\\operatorname{T}_{(10, )} R', InvalidTopNOrderByError),
        ('\\operatorname{T}_{(10, 123)} R', InvalidTopNOrderByError),
    ],
)
def test_syntax_errors(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
