from queries.services.ra.parser.ast import (
    RAQuery,
)
from queries.services.sql.scope.query import SelectScope, SetOperationScope, SQLScope

from .select import SelectTranspiler
from .set_operation import SetOperationTranspiler


class QueryTranspiler:
    @staticmethod
    def transpile(scope: SQLScope) -> RAQuery:
        match scope:
            case SelectScope():
                return SelectTranspiler().transpile(scope)
            case SetOperationScope():
                return SetOperationTranspiler().transpile(scope)
            case _:
                raise NotImplementedError(f'Unsupported scope type: {type(scope)}')
