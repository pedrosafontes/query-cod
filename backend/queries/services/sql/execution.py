from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.execution import execute_sql as execute_sql_service
from databases.types import QueryResult

from ..types import SQLStatement


def execute_sql(ast: SQLStatement, db: DatabaseConnectionInfo) -> QueryResult:
    return execute_sql_service(ast.sql(), db)
