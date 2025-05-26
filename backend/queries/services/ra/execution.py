from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.execution import execute_sql
from databases.services.schema import get_schema
from databases.types import QueryResult
from queries.services.types import to_relational_schema

from .ast import RAQuery
from .transpiler import RAtoSQLTranspiler


def execute_ra(ast: RAQuery, db: DatabaseConnectionInfo) -> QueryResult:
    schema = to_relational_schema(get_schema(db))
    select = RAtoSQLTranspiler(schema).transpile(ast)
    return execute_sql(select.sql(), db)
