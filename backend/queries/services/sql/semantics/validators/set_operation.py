from queries.services.types import RelationalSchema

from ..errors import (
    ColumnCountMismatchError,
    ColumnTypeMismatchError,
    TypeMismatchError,
)
from ..scope import Scope
from ..scope.projections import ProjectionsScope
from ..types import SetOperation
from ..utils import assert_comparable


class SetOperationValidator:
    def __init__(self, schema: RelationalSchema, scope: Scope) -> None:
        from .query import SQLSemanticAnalyzer

        self.scope = scope
        self.query_validator = SQLSemanticAnalyzer(schema)

    def validate(self, query: SetOperation) -> ProjectionsScope:
        left = self.query_validator.validate(query.left, self.scope)
        right = self.query_validator.validate(query.right, self.scope)

        if (l_len := len(left.types)) != (r_len := len(right.types)):
            raise ColumnCountMismatchError(query.right, l_len, r_len)

        for i, (lt, rt) in enumerate(zip(left.types, right.types, strict=True)):
            try:
                assert_comparable(lt, rt, query)
            except TypeMismatchError:
                raise ColumnTypeMismatchError(query, lt, rt, i) from None

        return left
