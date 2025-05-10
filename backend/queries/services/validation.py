from databases.utils.conversion import from_model

from ..models import Query
from ..types import QueryError
from .ra.validation import validate_ra
from .sql.validation import validate_sql
from .types import QueryAST


def validate_query(query: Query) -> tuple[QueryAST | None, list[QueryError]]:
    db = from_model(query.project.database)
    match query.language:
        case Query.QueryLanguage.SQL:
            return validate_sql(query.sql_text, db)
        case Query.QueryLanguage.RA:
            return validate_ra(query.ra_text, db)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')
