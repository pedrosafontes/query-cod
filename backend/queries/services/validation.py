from ..models import AbstractQuery as Query
from ..models import Language
from ..types import QueryError
from .ra.validation import validate_ra
from .sql.validation import validate_sql
from .types import QueryAST


def validate_query(query: Query) -> tuple[QueryAST | None, list[QueryError]]:
    match query.language:
        case Language.SQL:
            return validate_sql(query.query, query.database)
        case Language.RA:
            return validate_ra(query.query, query.database)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
