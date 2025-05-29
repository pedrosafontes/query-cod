from typing import cast

from queries.models import AbstractQuery as Query
from queries.models import Language

from .ra.ast import RAQuery
from .ra.transpiler import RAtoSQLTranspiler
from .sql.transpiler import SQLtoRATranspiler
from .types import SQLQuery, to_relational_schema


def transpile_query(query: Query) -> str | None:
    if not query.is_valid:
        return None

    schema = to_relational_schema(query.database.schema)
    match query.language:
        case Language.SQL:
            return SQLtoRATranspiler(schema).transpile(cast(SQLQuery, query.ast)).latex()

        case Language.RA:
            return RAtoSQLTranspiler(schema).transpile(cast(RAQuery, query.ast)).sql(pretty=True)
