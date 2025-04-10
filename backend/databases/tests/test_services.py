from unittest.mock import MagicMock, patch

import pytest
from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql


@pytest.fixture
def mock_db_info():
    return DatabaseConnectionInfo(
        database_type='postgresql',
        host='localhost',
        port=5432,
        user='test',
        password='secret',
        name='test_db',
    )


@pytest.fixture
def mock_sql_engine():
    mock_engine = MagicMock()
    mock_conn = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_conn.execute.return_value = mock_result

    mock_result.fetchall.return_value = [(1, 'Alice'), (2, 'Bob')]
    mock_result.keys.return_value = ['id', 'name']

    return {
        'engine': mock_engine,
        'connection': mock_conn,
        'result': mock_result,
    }


def test_execute_sql_success(mock_db_info, mock_sql_engine):
    with patch(
        'databases.models.database_connection_info.create_engine',
        return_value=mock_sql_engine['engine'],
    ):
        result = execute_sql('SELECT * FROM users', mock_db_info)

    mock_sql_engine['connection'].execute.assert_called_once()
    assert result['columns'] == ['id', 'name']
    assert result['rows'] == [[1, 'Alice'], [2, 'Bob']]


def test_execute_sql_empty_result(mock_db_info, mock_sql_engine):
    mock_sql_engine['result'].fetchall.return_value = []

    with patch(
        'databases.models.database_connection_info.create_engine',
        return_value=mock_sql_engine['engine'],
    ):
        result = execute_sql('SELECT * FROM users WHERE id = 999', mock_db_info)

    assert result['columns'] == ['id', 'name']
    assert result['rows'] == []
