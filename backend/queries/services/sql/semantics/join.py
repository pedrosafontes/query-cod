from queries.services.types import Attributes, RelationalSchema, flatten, merge_common_column
from sqlglot.expressions import Identifier, Join

from ..scope import SelectScope
from .errors import (
    ColumnNotFoundError,
    InvalidJoinConditionError,
    MissingJoinConditionError,
)
from .expression import ExpressionValidator
from .table import TableValidator
from .utils import assert_comparable


class JoinValidator:
    def __init__(
        self,
        scope: SelectScope,
    ) -> None:
        self.scope = scope
        self.expr_validator = ExpressionValidator(scope)
        self.table_validator = TableValidator(scope)

    def validate(self, left_schema: RelationalSchema, join: Join) -> RelationalSchema:
        table = join.this
        self.table_validator.validate(table)

        left_cols = flatten(left_schema)
        right_schema = self.scope.get_schema(table)
        right_cols = flatten(right_schema)

        join_schema = left_schema | right_schema

        kind = join.method or join.args.get('kind', 'INNER')
        using: list[Identifier] | None = join.args.get('using')
        condition = join.args.get('on')

        if using or kind == 'NATURAL':
            shared_columns = list(set(left_cols) & set(right_cols))
            join_columns = [ident.name for ident in using] if using else shared_columns
            self._validate_join_columns(join_columns, left_cols, right_cols, join)

            for col in join_columns:
                merge_common_column(join_schema, col)
        elif kind == 'CROSS':
            # CROSS JOINS must not have a condition
            if condition:
                raise InvalidJoinConditionError(condition)
        else:
            # INNER, LEFT, RIGHT, and FULL OUTER joins must have a condition
            if not condition:
                raise MissingJoinConditionError(join)
            self.expr_validator.validate_boolean(condition)

        return join_schema

    def _validate_join_columns(
        self, join_columns: list[str], left: Attributes, right: Attributes, join: Join
    ) -> None:
        for col in join_columns:
            if col not in left:
                raise ColumnNotFoundError.from_expression(join, col)
            assert_comparable(left[col], right[col], join)
