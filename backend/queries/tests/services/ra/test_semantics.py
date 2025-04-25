import pytest
from databases.types import DataType, Schema
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
from queries.services.ra.semantics.errors import (
    AmbiguousAttributeError,
    DivisionSchemaMismatchError,
    DivisionTypeMismatchError,
    InvalidFunctionArgumentError,
    TypeMismatchError,
    UndefinedAttributeError,
    UndefinedRelationError,
    UnionCompatibilityError,
)
from queries.services.ra.semantics import RASemanticAnalyzer


@pytest.fixture
def schema() -> Schema:
    return {
        'R': {'A': DataType.INTEGER, 'B': DataType.VARCHAR, 'C': DataType.FLOAT},
        'S': {'D': DataType.INTEGER, 'E': DataType.VARCHAR, 'F': DataType.FLOAT},
        'T': {'A': DataType.INTEGER, 'G': DataType.VARCHAR, 'H': DataType.BOOLEAN},
        'U': {'A': DataType.INTEGER, 'B': DataType.VARCHAR, 'C': DataType.FLOAT},
        'V': {'A': DataType.VARCHAR, 'B': DataType.VARCHAR},
        'Employee': {
            'id': DataType.INTEGER,
            'name': DataType.VARCHAR,
            'department': DataType.VARCHAR,
            'salary': DataType.FLOAT,
        },
        'Department': {
            'id': DataType.INTEGER,
            'name': DataType.VARCHAR,
            'manager_id': DataType.INTEGER,
        },
    }


@pytest.mark.parametrize(
    'expr',
    [
        Relation('R'),
        Projection([Attribute('A'), Attribute('B')], Relation('R')),
        Selection(Comparison(ComparisonOperator.GREATER_THAN, Attribute('A'), 10), Relation('R')),
        Join(JoinOperator.NATURAL, Relation('R'), Relation('S')),
        SetOperation(SetOperator.CARTESIAN, Relation('R'), Relation('S')),
        SetOperation(SetOperator.UNION, Relation('R'), Relation('U')),
        SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('U')),
        SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('U')),
        GroupedAggregation(
            group_by=[Attribute('A')],
            aggregations=[Aggregation(Attribute('B'), AggregationFunction.COUNT, 'X')],
            expression=Relation('R'),
        ),
        TopN(10, Attribute('A'), Relation('R')),
        ThetaJoin(
            Relation('Employee'),
            Relation('Department'),
            Comparison(
                ComparisonOperator.EQUAL,
                Attribute('department', 'Employee'),
                Attribute('name', 'Department'),
            ),
        ),
        Projection(
            [Attribute('A'), Attribute('B')],
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('C'), 5.0),
                Relation('R'),
            ),
        ),
        Projection(
            attributes=[
                Attribute('name'),
                Attribute('salary'),
            ],
            expression=Selection(
                condition=BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.AND,
                    left=Comparison(
                        operator=ComparisonOperator.EQUAL,
                        left=Attribute('department'),
                        right='IT',
                    ),
                    right=Comparison(
                        operator=ComparisonOperator.GREATER_THAN,
                        left=Attribute('salary'),
                        right=50000,
                    ),
                ),
                expression=Relation('Employee'),
            ),
        ),
    ],
)
def test_valid_ast_expressions(expr: RAExpression, schema: Schema) -> None:
    analyzer = RASemanticAnalyzer(schema)
    analyzer.validate(expr)


@pytest.mark.parametrize(
    'expr, expected_exception',
    [
        (Relation('X'), UndefinedRelationError),
        (
            Join(JoinOperator.NATURAL, Relation('R'), Relation('X')),
            UndefinedRelationError,
        ),
        (Projection([Attribute('Z')], Relation('R')), UndefinedAttributeError),
        (
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('Z'), 10),
                Relation('R'),
            ),
            UndefinedAttributeError,
        ),
        (
            Selection(Comparison(ComparisonOperator.EQUAL, Attribute('B'), 10), Relation('R')),
            TypeMismatchError,
        ),
        (
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('A'), 'text'), Relation('R')
            ),
            TypeMismatchError,
        ),
        (
            SetOperation(SetOperator.UNION, Relation('R'), Relation('S')),
            UnionCompatibilityError,
        ),
        (
            SetOperation(SetOperator.INTERSECT, Relation('R'), Relation('S')),
            UnionCompatibilityError,
        ),
        (
            SetOperation(SetOperator.DIFFERENCE, Relation('R'), Relation('S')),
            UnionCompatibilityError,
        ),
        (
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('A'), Attribute('G')),
            ),
            UndefinedAttributeError,
        ),
        (
            ThetaJoin(
                Relation('R'),
                Relation('S'),
                Comparison(ComparisonOperator.EQUAL, Attribute('B'), Attribute('D')),
            ),
            TypeMismatchError,
        ),
        (
            GroupedAggregation(
                [Attribute('Z')],
                [Aggregation(Attribute('A'), AggregationFunction.SUM, 'X')],
                Relation('R'),
            ),
            UndefinedAttributeError,
        ),
        (
            GroupedAggregation(
                [Attribute('A')],
                [Aggregation(Attribute('Z'), AggregationFunction.SUM, 'X')],
                Relation('R'),
            ),
            UndefinedAttributeError,
        ),
        (
            GroupedAggregation(
                group_by=[Attribute('A')],
                aggregations=[
                    Aggregation(
                        input=Attribute('B'),
                        aggregation_function=AggregationFunction.SUM,
                        output='X',
                    )
                ],
                expression=Relation('R'),
            ),
            InvalidFunctionArgumentError,
        ),
        (TopN(10, Attribute('Z'), Relation('R')), UndefinedAttributeError),
        (
            ThetaJoin(
                Relation('R'),
                Relation('T'),
                Comparison(ComparisonOperator.EQUAL, Attribute('A'), Attribute('B')),
            ),
            AmbiguousAttributeError,
        ),
        (
            Projection(
                [Attribute('A')],
                SetOperation(
                    SetOperator.CARTESIAN,
                    Relation('R'),
                    Relation('T'),
                ),
            ),
            AmbiguousAttributeError,
        ),
        (
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('A'), 10),
                SetOperation(
                    SetOperator.CARTESIAN,
                    Relation('R'),
                    Relation('T'),
                ),
            ),
            AmbiguousAttributeError,
        ),
        # AND between non-booleans
        (
            Selection(
                BinaryBooleanExpression(
                    BinaryBooleanOperator.AND,
                    Attribute('A'),
                    Attribute('B'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Logical NOT on a VARCHAR: ¬B
        (
            Selection(
                NotExpression(Attribute('B')),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Comparison between TEXT and FLOAT: B < C
        (
            Selection(
                Comparison(
                    ComparisonOperator.LESS_THAN,
                    Attribute('B'),
                    Attribute('C'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Comparison between INTEGER and TEXT: A = B
        (
            Selection(
                Comparison(
                    ComparisonOperator.EQUAL,
                    Attribute('A'),
                    Attribute('B'),
                ),
                Relation('R'),
            ),
            TypeMismatchError,
        ),
        # Right schema attributes must be subset of left
        (
            Division(
                dividend=Relation('R'),
                divisor=Relation('S'),
            ),
            DivisionSchemaMismatchError,
        ),
        # Attribute types must match
        (
            Division(
                dividend=Relation('R'),
                divisor=Relation('V'),
            ),
            DivisionTypeMismatchError,
        ),
    ],
)
def test_semantic_exceptions(
    expr: RAExpression, expected_exception: type[Exception], schema: Schema
) -> None:
    with pytest.raises(expected_exception):
        RASemanticAnalyzer(schema).validate(expr)


@pytest.mark.parametrize(
    'function',
    [
        AggregationFunction.SUM,
        AggregationFunction.AVG,
    ],
)
def test_aggregation_function_invalid_on_VARCHAR(
    function: AggregationFunction, schema: Schema
) -> None:
    expr = GroupedAggregation(
        group_by=[Attribute('A')],
        aggregations=[Aggregation(Attribute('B'), function, 'X')],  # B is VARCHAR
        expression=Relation('R'),
    )

    with pytest.raises(InvalidFunctionArgumentError):
        RASemanticAnalyzer(schema).validate(expr)


@pytest.mark.parametrize(
    'function, attribute_name',
    [
        (AggregationFunction.SUM, 'A'),  # INTEGER
        (AggregationFunction.AVG, 'A'),  # INTEGER
        (AggregationFunction.MIN, 'A'),  # INTEGER
        (AggregationFunction.MAX, 'A'),  # INTEGER
        (AggregationFunction.SUM, 'C'),  # FLOAT
        (AggregationFunction.AVG, 'C'),  # FLOAT
        (AggregationFunction.MIN, 'C'),  # FLOAT
        (AggregationFunction.MAX, 'C'),  # FLOAT
        (AggregationFunction.COUNT, 'A'),  # any type is fine
        (AggregationFunction.COUNT, 'B'),
        (AggregationFunction.COUNT, 'C'),
    ],
)
def test_aggregation_function_valid_on_compatible_types(
    function: AggregationFunction, attribute_name: str, schema: Schema
) -> None:
    expr = GroupedAggregation(
        group_by=[Attribute('B')],
        aggregations=[Aggregation(Attribute(attribute_name), function, 'X')],
        expression=Relation('R'),
    )

    analyzer = RASemanticAnalyzer(schema)
    analyzer.validate(expr)  # should not raise
