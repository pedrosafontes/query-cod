import pytest
from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    Comparison,
    ComparisonOperator,
    Projection,
    RAExpression,
    Relation,
    Selection,
)
from queries.services.ra.semantics import RASemanticAnalyzer
from queries.services.types import RelationalSchema


@pytest.mark.parametrize(
    'expr',
    [
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
def test_valid_complex_queries(expr: RAExpression, schema: RelationalSchema) -> None:
    analyzer = RASemanticAnalyzer(schema)
    analyzer.validate(expr)
