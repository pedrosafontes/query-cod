from ..models import AbstractQuery as Query
from ..types import QueryError
from .ra.validation import validate_ra
from .sql.validation import validate_sql
from .types import QueryAST


def validate_query(query: Query) -> tuple[QueryAST | None, list[QueryError]]:
    match query.language:
        case Query.Language.SQL:
            return validate_sql(query.text, query.database)
        case Query.Language.RA:
            return validate_ra(query.text, query.database)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
