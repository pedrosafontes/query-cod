from collections.abc import Callable
from typing import Any

import pytest
from queries.services.ra.parser.ast import RAQuery
from queries.services.ra.transpiler import RAtoSQLTranspiler
from queries.services.sql.parser import parse_sql
from queries.services.sql.transpiler.transpilers import SQLtoRATranspiler
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
        'rotation': {
            'employee_id': DataType.INTEGER,
            'dept_id': DataType.INTEGER,
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
        'rotation': [
            {'employee_id': 1, 'dept_id': 1},
            {'employee_id': 1, 'dept_id': 2},
            {'employee_id': 2, 'dept_id': 1},
            {'employee_id': 3, 'dept_id': 1},
            {'employee_id': 3, 'dept_id': 2},
        ],
    }


@pytest.fixture
def assert_equivalent(
    schema: RelationalSchema, data: dict[str, list[dict[str, Any]]]
) -> Callable[[str, RAQuery], None]:
    sqlglot_schema = to_sqlglot_schema(schema)

    def _assert_equivalent(sql_text: str, expected_ra: RAQuery) -> None:
        ra = SQLtoRATranspiler(schema).transpile(parse_sql(sql_text))
        print(ra)
        sql = RAtoSQLTranspiler(schema, distinct=False).transpile(ra)
        print(sql.sql())
        expected_sql = RAtoSQLTranspiler(schema, distinct=False).transpile(expected_ra)
        assert _tables_equal(
            execute(sql, tables=data, schema=sqlglot_schema),
            execute(expected_sql, tables=data, schema=sqlglot_schema),
        )
        assert _tables_equal(
            execute(sql, tables=data, schema=sqlglot_schema),
            execute(sql_text, tables=data, schema=sqlglot_schema),
        )

    return _assert_equivalent


def _tables_equal(t1: Table, t2: Table) -> bool:
    print(t1)
    print(t2)
    return t1.columns == t2.columns and t1.rows == t2.rows
