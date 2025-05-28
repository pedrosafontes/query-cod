from databases.models import Database
from queries.types import QueryError

from ..types import to_relational_schema
from .ast import RAQuery
from .parser import parse_ra
from .parser.errors import RASyntaxError
from .semantics import validate_ra_semantics


def validate_ra(query_text: str, db: Database) -> tuple[RAQuery | None, list[QueryError]]:
    if not query_text.strip():
        return None, []

    try:
        query = parse_ra(query_text)
    except RASyntaxError as e:
        syntax_error: QueryError = {'title': e.title}
        if e.description:
            syntax_error['description'] = e.description
        return None, [syntax_error]

    schema = to_relational_schema(db.schema)
    return query, validate_ra_semantics(query, schema)
