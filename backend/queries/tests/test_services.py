import pytest
from databases.models import DatabaseConnectionInfo
from queries.services.sql_parser import parse_sql
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def db_info():
    return DatabaseConnectionInfo(
        database_type='postgresql',
        host='localhost',
        port=5432,
        user='user',
        password='secret',
        name='test_db',
    )


def test_empty_query_returns_invalid(db_info):
    result = parse_sql("   ", db_info)
    assert result == {"valid": False, "errors": []}


def test_invalid_syntax_returns_errors(db_info):
    result = parse_sql("SELEC FROM", db_info)
    assert result["valid"] is False
    assert len(result["errors"]) >= 1
    assert "message" in result["errors"][0]


def test_disallowed_statement_returns_error(db_info):
    result = parse_sql("DELETE FROM users", db_info)
    assert result["valid"] is False
    assert "Only SELECT queries are allowed." in result["errors"][0]["message"]


def test_semantic_error(monkeypatch, db_info):
    def mock_execute_sql(sql, db):
        raise SQLAlchemyError("relation 'users' does not exist")

    monkeypatch.setattr("queries.services.sql_parser.execute_sql", mock_execute_sql)

    result = parse_sql("SELECT * FROM users", db_info)
    assert result["valid"] is False
    assert "Semantic error" in result["errors"][0]["message"]


def test_valid_query(monkeypatch, db_info):
    monkeypatch.setattr("queries.services.sql_parser.execute_sql", lambda sql, db: {"columns": [], "rows": []})
    result = parse_sql("SELECT 1", db_info)
    assert result["valid"] is True
