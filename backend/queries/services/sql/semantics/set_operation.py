from ..scope import SetOperationScope
from .errors import (
    ColumnCountMismatchError,
    ColumnTypeMismatchError,
    TypeMismatchError,
)
from .utils import assert_comparable


class SetOperationValidator:
    @staticmethod
    def validate(scope: SetOperationScope) -> None:
        from .query import QueryValidator

        QueryValidator.validate(scope.left)
        QueryValidator.validate(scope.right)

        left_types = scope.left.projections.types
        right_types = scope.right.projections.types

        if (l_len := len(left_types)) != (r_len := len(right_types)):
            raise ColumnCountMismatchError(scope.set_operation.right, l_len, r_len)

        for i, (lt, rt) in enumerate(zip(left_types, right_types, strict=True)):
            try:
                assert_comparable(lt, rt, scope.set_operation)
            except TypeMismatchError:
                raise ColumnTypeMismatchError(scope.set_operation, lt, rt, i) from None
