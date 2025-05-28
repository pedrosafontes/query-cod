from databases.models.database import Database
from databases.services.execution import execute_sql as execute_sql_service
from databases.types import QueryResult

from ..types import SQLQuery


def execute_sql(ast: SQLQuery, db: Database) -> QueryResult:
    return execute_sql_service(ast.sql(), db.connection_info)
