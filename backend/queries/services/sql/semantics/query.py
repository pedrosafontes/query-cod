from ..scope import SelectScope, SetOperationScope, SQLScope
from .select import SelectValidator
from .set_operation import SetOperationValidator


class QueryValidator:
    def validate(self, scope: SQLScope) -> None:
        match scope:
            case SelectScope():
                SelectValidator(scope).validate()
            case SetOperationScope():
                SetOperationValidator(scope).validate()
