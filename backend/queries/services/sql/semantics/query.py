from ..scope import DerivedTableScope, SelectScope, SetOperationScope, SQLScope
from .select import SelectValidator
from .set_operation import SetOperationValidator


class QueryValidator:
    @staticmethod
    def validate(scope: SQLScope) -> None:
        match scope:
            case SelectScope():
                SelectValidator.validate(scope)
            case SetOperationScope():
                SetOperationValidator.validate(scope)
            case DerivedTableScope():
                QueryValidator.validate(scope.child)
