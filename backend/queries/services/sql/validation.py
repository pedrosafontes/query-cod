from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql
from databases.services.schema import get_schema
from queries.services.sql.parser import parse_sql
from queries.types import QueryError, QueryValidationResult
from queries.utils.tokens import to_error_position
from sqlalchemy.exc import SQLAlchemyError
from sqlglot import ParseError

from ..types import to_relational_schema
from .semantics import SQLSemanticAnalyzer
from .semantics.errors import SQLSemanticError


def validate_sql(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    if not query_text.strip():
        return {'valid': False}

    # Check for syntax errors
    try:
        tree = parse_sql(query_text)
    except ParseError as e:
        syntax_errors: list[QueryError] = [
            {
                'title': 'Syntax Error',
                'description': err['description'],
                'position': to_error_position(err['line'], err['col'], len(err['highlight'])),
            }
            for err in e.errors
        ]

        return {'valid': False, 'errors': syntax_errors}

    # Check for semantic errors
    try:
        schema = to_relational_schema(get_schema(db))
        SQLSemanticAnalyzer(schema).validate(tree)
    except SQLSemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.hint:
            semantic_error['hint'] = e.hint
        return {'valid': False, 'errors': [semantic_error]}

    try:
        execute_sql(f'EXPLAIN {query_text}', db)
    except SQLAlchemyError as e:
        explain_error: QueryError = {
            'title': 'Error during EXPLAIN',
            'description': str(e),
        }
        return {'valid': False, 'errors': [explain_error]}

    return {'valid': True}
