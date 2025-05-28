from ..models import Query
from ..types import QueryError
from .ra.validation import validate_ra
from .sql.validation import validate_sql
from .types import QueryAST


def validate_query(query: Query) -> tuple[QueryAST | None, list[QueryError]]:
    match query.language:
        case Query.Language.SQL:
            return validate_sql(query.text, query.project.database)
        case Query.Language.RA:
            return validate_ra(query.text, query.project.database)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
