from queries.services.ra.parser.ast import (
    RAQuery,
)

from ..scope.query import SelectScope, SetOperationScope, SQLScope
from .select import transpile_select
from .set_operation import transpile_set_operation


def transpile_query(scope: SQLScope) -> RAQuery:
    match scope:
        case SelectScope():
            return transpile_select(scope)
        case SetOperationScope():
            return transpile_set_operation(scope)
        case _:
            raise NotImplementedError(f'Unsupported scope type: {type(scope)}')
