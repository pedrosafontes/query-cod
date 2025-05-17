from queries.services.ra.parser.ast import (
    RAQuery,
)
from queries.services.types import SQLQuery
from sqlglot.expressions import Select

from .select import SelectTranspiler


class SQLtoRATranspiler:
    def transpile(self, query: SQLQuery) -> RAQuery:
        match query:
            case Select():
                return SelectTranspiler().transpile(query)
            # case query if isinstance(query, SetOperation):
            #     return self._transpile_set_operation(query)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')
