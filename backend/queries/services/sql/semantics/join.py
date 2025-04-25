from databases.types import Schema, TableSchema
from sqlglot.expressions import Identifier, Join

from .errors import (
    CrossJoinConditionError,
    MissingJoinConditionError,
    NoCommonColumnsError,
    UndefinedColumnError,
)
from .expression import ExpressionValidator
from .scope import Scope
from .source import SourceValidator
from .type_utils import assert_boolean, assert_comparable
from .types import ColumnTypes


class JoinValidator:
    def __init__(
        self,
        schema: Schema,
        scope: Scope,
        expr_validator: ExpressionValidator,
    ) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.expr_validator = expr_validator
        self.query_validator = QueryValidator(schema)
        self.source_validator = SourceValidator(schema, scope)

    def validate_join(self, join: Join) -> None:
        left_cols = self.scope.sources.snapshot_columns()
        self.source_validator.validate(join.this)
        right_cols = self.schema[join.this.name]

        kind = join.method or join.args.get('kind', 'INNER')
        using = join.args.get('using')
        condition = join.args.get('on')

        if using:
            self._validate_using(using, left_cols, right_cols)
        elif kind == 'NATURAL':
            self._validate_natural_join(left_cols, right_cols)
        elif kind == 'CROSS':
            # CROSS JOINS must not have a condition
            if condition:
                raise CrossJoinConditionError()
        else:
            # INNER, LEFT, RIGHT, and FULL OUTER joins must have a condition
            if not condition:
                raise MissingJoinConditionError()
            assert_boolean(self.expr_validator.validate_basic(condition))

    def _validate_using(
        self, using: list[Identifier], left: ColumnTypes, right: TableSchema
    ) -> None:
        # All columns in USING must be present in both tables
        for ident in using:
            col = ident.name
            if col not in left:
                raise UndefinedColumnError(col)
            for ltype in left[col]:
                assert_comparable(ltype, right[col])

    def _validate_natural_join(self, left: ColumnTypes, right: TableSchema) -> None:
        shared = set(left) & set(right)
        # NATURAL JOIN must have at least one common column
        if not shared:
            raise NoCommonColumnsError()
        # All common columns must be comparable
        for col in shared:
            for ltype in left[col]:
                assert_comparable(ltype, right[col])
