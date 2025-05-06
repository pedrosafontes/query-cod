from collections.abc import Callable
from typing import Any

import pytest
from queries.services.ra.execution.transpiler import RAtoSQLTranspiler
from queries.services.ra.parser.ast import RAExpression
from queries.services.types import RelationalSchema, to_sqlglot_schema
from ra_sql_visualisation.types import DataType
from sqlglot.executor import execute
from sqlglot.executor.table import Table


@pytest.fixture
def schema() -> RelationalSchema:
    return {
        'department': {
            'dept_id': DataType.INTEGER,
            'dept_name': DataType.VARCHAR,
        },
        'employee': {
            'id': DataType.INTEGER,
            'name': DataType.VARCHAR,
            'age': DataType.INTEGER,
            'dept_id': DataType.INTEGER,
            'senior': DataType.BOOLEAN,
        },
    }


@pytest.fixture
def data() -> dict[str, list[dict[str, Any]]]:
    return {
        'department': [
            {'dept_id': 1, 'dept_name': 'HR'},
            {'dept_id': 2, 'dept_name': 'Engineering'},
        ],
        'employee': [
            {'id': 1, 'name': 'Alice', 'age': 30, 'dept_id': 1, 'senior': False},
            {'id': 2, 'name': 'Bob', 'age': 25, 'dept_id': 2, 'senior': False},
            {'id': 3, 'name': 'Carol', 'age': 40, 'dept_id': 1, 'senior': True},
        ],
    }


@pytest.fixture
def assert_equivalent(
    schema: RelationalSchema, data: dict[str, list[dict[str, Any]]]
) -> Callable[[RAExpression, str], None]:
    sqlglot_schema = to_sqlglot_schema(schema)

    def _assert_equivalent(ra_ast: RAExpression, expected_sql: str) -> None:
        sql = RAtoSQLTranspiler(schema).transpile(ra_ast)
        print(sql.sql())
        assert _tables_equal(
            execute(sql, tables=data, schema=sqlglot_schema),
            execute(expected_sql, tables=data, schema=sqlglot_schema),
        )

    return _assert_equivalent


def _tables_equal(t1: Table, t2: Table) -> bool:
    return t1.columns == t2.columns and t1.rows == t2.rows
