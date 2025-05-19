from ..errors import (
    ColumnCountMismatchError,
    ColumnTypeMismatchError,
    TypeMismatchError,
)
from ..scope import SetOperationScope
from ..utils import assert_comparable


class SetOperationValidator:
    def __init__(self, scope: SetOperationScope) -> None:
        self.scope = scope
        self.set_operation = scope.query

    def validate(self) -> None:
        from .query import QueryValidator

        QueryValidator().validate(self.scope.left)
        QueryValidator().validate(self.scope.right)

        left_types = self.scope.left.projections.types
        right_types = self.scope.right.projections.types

        if (l_len := len(left_types)) != (r_len := len(right_types)):
            raise ColumnCountMismatchError(self.set_operation.right, l_len, r_len)

        for i, (lt, rt) in enumerate(zip(left_types, right_types, strict=True)):
            try:
                assert_comparable(lt, rt, self.set_operation)
            except TypeMismatchError:
                raise ColumnTypeMismatchError(self.set_operation, lt, rt, i) from None
