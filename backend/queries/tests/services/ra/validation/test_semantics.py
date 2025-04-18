import pytest
from databases.types import DataType, Schema
from queries.services.ra.parser.ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    Comparison,
    ComparisonOperator,
    Division,
    GroupedAggregation,
    Join,
    JoinOperator,
    Projection,
    RAExpression,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from queries.services.ra.validation.errors import (
    AmbiguousAttributeError,
    DivisionSchemaMismatchError,
    DivisionTypeMismatchError,
    InvalidFunctionArgumentError,
    TypeMismatchError,
    UndefinedAttributeError,
    UndefinedRelationError,
    UnionCompatibilityError,
)
from queries.services.ra.validation.semantics import RASemanticAnalyzer


@pytest.fixture
def mock_schema() -> Schema:
    return {
        'R': {'A': DataType.INTEGER, 'B': DataType.STRING, 'C': DataType.FLOAT},
        'S': {'D': DataType.INTEGER, 'E': DataType.STRING, 'F': DataType.FLOAT},
        'T': {'A': DataType.INTEGER, 'G': DataType.STRING, 'H': DataType.BOOLEAN},
        'U': {'A': DataType.INTEGER, 'B': DataType.STRING, 'C': DataType.FLOAT},
        'V': {'A': DataType.STRING, 'B': DataType.STRING},
        'Employee': {
            'id': DataType.INTEGER,
            'name': DataType.STRING,
            'department': DataType.STRING,
            'salary': DataType.FLOAT,
        },
        'Department': {
            'id': DataType.INTEGER,
            'name': DataType.STRING,
            'manager_id': DataType.INTEGER,
        },
    }


class TestRAValidation:
    @pytest.mark.parametrize(
        'expr',
        [
            Relation('R'),
            Projection([Attribute('A'), Attribute('B')], Relation('R')),
            Selection(
                Comparison(ComparisonOperator.GREATER_THAN, Attribute('A'), 10), Relation('R')
            ),
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
        ],
    )
    def test_valid_ast_expressions(self, expr: RAExpression, mock_schema: Schema) -> None:
        analyzer = RASemanticAnalyzer(mock_schema)
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
                    group_by=[Attribute("A")],
                    aggregations=[
                        Aggregation(
                            input=Attribute("B"),
                            aggregation_function=AggregationFunction.SUM,
                            output="X"
                        )
                    ],
                    expression=Relation("R")
                ),
                InvalidFunctionArgumentError,
            ),
            (TopN(10, Attribute('Z'), Relation('R')), UndefinedAttributeError),
        ],
    )
    def test_semantic_exceptions(
        self, expr: RAExpression, expected_exception: type[Exception], mock_schema: Schema
    ) -> None:
        analyzer = RASemanticAnalyzer(mock_schema)
        with pytest.raises(expected_exception):
            analyzer.validate(expr)

    @pytest.mark.parametrize(
        'expr, expected_exception',
        [
            (
                ThetaJoin(
                    Relation('R'),
                    Relation('T'),
                    Comparison(ComparisonOperator.EQUAL, Attribute('A'), Attribute('B')),
                ),
                AmbiguousAttributeError,
            ),
        ],
    )
    def test_ambiguous_attribute_exceptions(
        self, expr: RAExpression, expected_exception: type[Exception], mock_schema: Schema
    ) -> None:
        analyzer = RASemanticAnalyzer(mock_schema)
        with pytest.raises(expected_exception):
            analyzer.validate(expr)

@pytest.mark.parametrize(
    "expr, expected_exception",
    [
        # Comparison between TEXT and FLOAT: B < C
        (
            Selection(
                Comparison(
                    ComparisonOperator.LESS_THAN,
                    Attribute("B"),
                    Attribute("C"),
                ),
                Relation("R"),
            ),
            TypeMismatchError,
        ),
        # Comparison between INTEGER and TEXT: A = B
        (
            Selection(
                Comparison(
                    ComparisonOperator.EQUAL,
                    Attribute("A"),
                    Attribute("B"),
                ),
                Relation("R"),
            ),
            TypeMismatchError,
        ),
    ],
)
def test_comparison_type_errors(
    expr: RAExpression, expected_exception: type[Exception], mock_schema: Schema
) -> None:
    analyzer = RASemanticAnalyzer(mock_schema)
    with pytest.raises(expected_exception):
        analyzer.validate(expr)

@pytest.mark.parametrize(
    "function",
    [
        AggregationFunction.SUM,
        AggregationFunction.AVG,
    ],
)
def test_aggregation_function_invalid_on_string(
    function: AggregationFunction, mock_schema: Schema
) -> None:
    expr = GroupedAggregation(
        group_by=[Attribute("A")],
        aggregations=[Aggregation(Attribute("B"), function, "X")],  # B is STRING
        expression=Relation("R"),
    )

    analyzer = RASemanticAnalyzer(mock_schema)
    with pytest.raises(InvalidFunctionArgumentError):
        analyzer.validate(expr)

@pytest.mark.parametrize(
    "function, attribute_name",
    [
        (AggregationFunction.SUM, "A"),   # INTEGER
        (AggregationFunction.AVG, "A"),   # INTEGER
        (AggregationFunction.MIN, "A"),   # INTEGER
        (AggregationFunction.MAX, "A"),   # INTEGER
        (AggregationFunction.SUM, "C"),   # FLOAT
        (AggregationFunction.AVG, "C"),   # FLOAT
        (AggregationFunction.MIN, "C"),   # FLOAT
        (AggregationFunction.MAX, "C"),   # FLOAT
        (AggregationFunction.COUNT, "A"),  # any type is fine
        (AggregationFunction.COUNT, "B"),
        (AggregationFunction.COUNT, "C"),
    ],
)
def test_aggregation_function_valid_on_compatible_types(
    function: AggregationFunction, attribute_name: str, mock_schema: Schema
) -> None:
    expr = GroupedAggregation(
        group_by=[Attribute("B")],
        aggregations=[Aggregation(Attribute(attribute_name), function, "X")],
        expression=Relation("R"),
    )

    analyzer = RASemanticAnalyzer(mock_schema)
    analyzer.validate(expr)  # should not raise

@pytest.mark.parametrize(
    "expr, expected_exception",
    [
        # Right schema attributes must be subset of left
        (
            Division(
                dividend=Relation("R"),
                divisor=Relation("S"),
            ),
            DivisionSchemaMismatchError,
        ),
        # Attribute types must match
        (
            Division(
                dividend=Relation("R"),
                divisor=Relation("V"),
            ),
            DivisionTypeMismatchError,
        ),
    ],
)
def test_division_operator_errors(
    expr: RAExpression, expected_exception: type[Exception], mock_schema: Schema
) -> None:
    analyzer = RASemanticAnalyzer(mock_schema)
    with pytest.raises(expected_exception):
        analyzer.validate(expr)
