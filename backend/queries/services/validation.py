from ..models import Query
from ..types import QueryError
from .ra.validation import validate_ra
from .sql.validation import validate_sql
from .types import QueryAST


def validate_query(query: Query) -> tuple[QueryAST | None, list[QueryError]]:
    db = query.project.database.connection_info
    match query.language:
        case Query.Language.SQL:
            return validate_sql(query.text, db)
        case Query.Language.RA:
            return validate_ra(query.text, db)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
