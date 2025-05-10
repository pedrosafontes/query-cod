from typing import NotRequired, TypedDict

from databases.types import QueryResult
from databases.utils.conversion import from_model
from queries.models import Query

from .ra.execution import execute_ra
from .ra.parser.ast import RAQuery
from .sql.execution import execute_sql
from .types import SQLQuery


class QueryExecutionResult(TypedDict):
    success: bool
    results: NotRequired[QueryResult]


def execute_query(query: Query) -> QueryExecutionResult:
    db = from_model(query.project.database)
    if not query.is_executable:
        return {'success': False}

    match query.ast:
        case sql_query if isinstance(sql_query, SQLQuery):
            return {'success': True, 'results': execute_sql(sql_query, db)}
        case RAQuery():
            return {'success': True, 'results': execute_ra(query.ast, db)}
        case _:
            raise ValueError(f'Unsupported query AST type: {type(query.ast)}')
