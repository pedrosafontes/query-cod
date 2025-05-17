from queries.services.ra.parser.ast import (
    RAQuery,
)
from queries.services.types import SQLQuery
from sqlglot.expressions import Select, SetOperation

from .select import SelectTranspiler
from .set_operation import SetOperationTranspiler


class SQLtoRATranspiler:
    def transpile(self, query: SQLQuery) -> RAQuery:
        match query:
            case Select():
                return SelectTranspiler().transpile(query)
            case query if isinstance(query, SetOperation):
                return SetOperationTranspiler().transpile(query)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')
