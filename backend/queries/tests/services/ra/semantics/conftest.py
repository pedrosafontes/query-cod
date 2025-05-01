from collections.abc import Callable

import pytest
from queries.services.ra.parser.ast import RAExpression
from queries.services.ra.semantics.analyzer import RASemanticAnalyzer
from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType


@pytest.fixture
def schema() -> RelationalSchema:
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


@pytest.fixture
def assert_valid(schema: RelationalSchema) -> Callable[[RAExpression], None]:
    def _assert_valid(query: RAExpression) -> None:
        RASemanticAnalyzer(schema).validate(query)

    return _assert_valid


@pytest.fixture
def assert_invalid(schema: RelationalSchema) -> Callable[[RAExpression, type[Exception]], None]:
    def _assert_invalid(query: RAExpression, expected_exception: type[Exception]) -> None:
        with pytest.raises(expected_exception):
            RASemanticAnalyzer(schema).validate(query)

    return _assert_invalid
