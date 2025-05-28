from databases.models import Database
from databases.services.execution import execute_sql
from queries.services.sql.parser import parse_sql
from queries.types import QueryError
from queries.utils.tokens import to_error_position
from sqlalchemy.exc import SQLAlchemyError
from sqlglot.errors import ParseError, SqlglotError

from ..types import SQLQuery, to_relational_schema
from .semantics import validate_sql_semantics


def validate_sql(query_text: str, db: Database) -> tuple[SQLQuery | None, list[QueryError]]:
    if not query_text.strip():
        return None, []

    # Check for syntax errors
    try:
        syntax_errors: list[QueryError] = []
        tree = parse_sql(query_text)
    except ParseError as e:
        for err in e.errors:
            syntax_errors.append(
                {
                    'title': 'Syntax Error',
                    'description': err['description'],
                    'position': to_error_position(err['line'], err['col'], len(err['highlight'])),
                }
            )
    except SqlglotError as e:
        syntax_errors.append(
            {
                'title': 'Syntax Error',
                'description': str(e),
            }
        )

    if syntax_errors:
        return None, syntax_errors

    # Check for semantic errors
    schema = to_relational_schema(db.schema)
    semantic_errors = validate_sql_semantics(tree, schema)
    if semantic_errors:
        return tree, semantic_errors

    try:
        execute_sql(f'EXPLAIN {query_text}', db.connection_info)
    except SQLAlchemyError as e:
        explain_error: QueryError = {
            'title': 'Error during EXPLAIN',
            'description': str(e),
        }
        return tree, [explain_error]

    return tree, []
