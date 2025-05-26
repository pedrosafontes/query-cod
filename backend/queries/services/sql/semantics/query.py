from ..scope import DerivedTableScope, SelectScope, SetOperationScope, SQLScope
from .select import validate_select
from .set_operation import validate_set_operation


def validate_query(scope: SQLScope) -> None:
    match scope:
        case SelectScope():
            validate_select(scope)
        case SetOperationScope():
            validate_set_operation(scope)
        case DerivedTableScope():
            validate_query(scope.child)
