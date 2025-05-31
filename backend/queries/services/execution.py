from databases.models.database import Database
from databases.types import QueryResult
from queries.models import AbstractQuery as Query

from .ra.ast import RAQuery
from .ra.execution import execute_ra
from .sql.execution import execute_sql
from .types import QueryAST, SQLQuery


def execute_query(query: Query) -> QueryResult | None:
    if not (query.is_valid and query.ast):
        return None

    return _execute(query.ast, query.database)


def execute_subquery(query: Query, subquery_id: int) -> QueryResult | None:
    subquery = query.subqueries.get(subquery_id)
    return _execute(subquery, query.database) if subquery else None


def _execute(ast: QueryAST, database: Database) -> QueryResult:
    match ast:
        case sql_query if isinstance(sql_query, SQLQuery):
            return execute_sql(sql_query, database)
        case RAQuery():
            return execute_ra(ast, database)
