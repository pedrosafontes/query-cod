from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema
from queries.types import QueryError

from ..types import to_relational_schema
from .parser import parse_ra
from .parser.ast import RAQuery
from .parser.errors import RASyntaxError
from .semantics import validate_ra_semantics


def validate_ra(
    query_text: str, db: DatabaseConnectionInfo
) -> tuple[RAQuery | None, list[QueryError]]:
    if not query_text.strip():
        return None, []

    try:
        query = parse_ra(query_text)
    except RASyntaxError as e:
        syntax_error: QueryError = {'title': e.title}
        if e.description:
            syntax_error['description'] = e.description
        return None, [syntax_error]

    schema = to_relational_schema(get_schema(db))
    return query, validate_ra_semantics(query, schema)
