from databases.utils.conversion import from_model

from ..models import Query
from ..types import QueryValidationResult
from .ra.validation import validate_ra
from .sql.validation import validate_sql


def validate_query(query: Query) -> QueryValidationResult:
    db = from_model(query.project.database)
    match query.language:
        case Query.QueryLanguage.SQL:
            result, _ = validate_sql(query.sql_text, db)
        case Query.QueryLanguage.RA:
            result, _ = validate_ra(query.ra_text, db)
        case _:
            raise ValueError(f'Unsupported query language: {query.language}')

    return result
