from databases.types import Schema
from sqlglot import Expression
from sqlglot.expressions import (
    Except,
    Intersect,
    Select,
    Union,
)

from .clause import ClauseValidator
from .errors import (
    ColumnCountMismatchError,
    ColumnTypeMismatchError,
    TypeMismatchError,
)
from .scope import Scope
from .scope.projection import ProjectionScope
from .type_utils import (
    assert_comparable,
)


class QueryValidator:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, query: Expression, outer_scope: Scope | None) -> ProjectionScope:
        match query:
            case Select():
                return self._validate_select(query, outer_scope)
            case Union() | Intersect() | Except():
                return self._validate_set_operation(query, outer_scope)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')

    def _validate_select(self, select: Select, outer_scope: Scope | None) -> ProjectionScope:
        # Validate all clauses of a SELECT statement in the order of execution
        scope = Scope(outer_scope)
        validator = ClauseValidator(self.schema, scope)

        validator.populate_from(select)
        validator.validate_joins(select)
        validator.validate_where(select)
        validator.validate_group_by(select)
        validator.validate_having(select)
        validator.validate_projection(select)
        validator.validate_order_by(select)
        return scope.projections

    def _validate_set_operation(
        self, query: Union | Intersect | Except, outer_scope: Scope | None
    ) -> ProjectionScope:
        left = self.validate(query.left, outer_scope)
        right = self.validate(query.right, outer_scope)

        if (l_len := len(left.types)) != (r_len := len(right.types)):
            raise ColumnCountMismatchError(l_len, r_len)

        for i, (lt, rt) in enumerate(zip(left.types, right.types, strict=True)):
            try:
                assert_comparable(lt, rt)
            except TypeMismatchError:
                raise ColumnTypeMismatchError(lt, rt, i) from None

        return left
