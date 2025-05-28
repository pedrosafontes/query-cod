from databases.models import Database
from databases.services.execution import execute_sql
from databases.types import QueryResult
from queries.services.types import to_relational_schema

from .ast import RAQuery
from .transpiler import RAtoSQLTranspiler


def execute_ra(ast: RAQuery, db: Database) -> QueryResult:
    schema = to_relational_schema(db.schema)
    select = RAtoSQLTranspiler(schema).transpile(ast)
    return execute_sql(select.sql(), db.connection_info)
