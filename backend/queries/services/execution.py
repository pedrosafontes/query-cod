from typing import NotRequired, TypedDict

from databases.types import QueryResult
from databases.utils.conversion import from_model
from queries.models import Query

from .ra.execution import execute_ra
from .ra.validation import validate_ra
from .sql.execution import execute_sql
from .sql.validation import validate_sql


class QueryExecutionResult(TypedDict):
    success: bool
    results: NotRequired[QueryResult]


def execute_query(query: Query) -> QueryExecutionResult:
    db = from_model(query.project.database)
    match query.language:
        case Query.QueryLanguage.SQL:
            result, sql_ast = validate_sql(query.sql_text, db)
            if result['executable'] and sql_ast:
                return {'success': True, 'results': execute_sql(sql_ast, db)}
            else:
                return {'success': False}
        case Query.QueryLanguage.RA:
            result, ra_ast = validate_ra(query.ra_text, db)
            if result['executable'] and ra_ast:
                return {'success': True, 'results': execute_ra(ra_ast, db)}
            else:
                return {'success': False}
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
