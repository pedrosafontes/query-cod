import pytest
from queries.services.ra.ast import (
    EQ,
    GT,
    And,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.ra.semantics.analyzer import RASemanticAnalyzer
from queries.services.types import RelationalSchema


@pytest.mark.parametrize(
    'query',
    [
        Relation('Employee')
        .select(And(EQ(attribute('department'), 'IT'), GT(attribute('salary'), 50000)))
        .project('name', 'salary'),
    ],
)
def test_valid_complex_queries(query: RAQuery, schema: RelationalSchema) -> None:
    analyzer = RASemanticAnalyzer(schema)
    analyzer.validate(query)
