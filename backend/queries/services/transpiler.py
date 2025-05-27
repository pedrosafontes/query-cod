from typing import cast

from databases.services.schema import get_schema
from queries.models import Query

from .ra.ast import RAQuery
from .ra.transpiler import RAtoSQLTranspiler
from .sql.transpiler import SQLtoRATranspiler
from .types import SQLQuery, to_relational_schema


def transpile_query(query: Query) -> str | None:  # type: ignore[return]
    if not query.is_valid:
        return None

    schema = to_relational_schema(get_schema(query.project.database.connection_info))
    match query.language:
        case Query.Language.SQL:
            return SQLtoRATranspiler(schema).transpile(cast(SQLQuery, query.ast)).latex()

        case Query.Language.RA:
            return RAtoSQLTranspiler(schema).transpile(cast(RAQuery, query.ast)).sql(pretty=True)
