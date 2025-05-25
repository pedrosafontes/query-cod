from queries.services.types import Attributes
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

    def validate(self, join: Join) -> None:
        table = join.this
        self.table_validator.validate(table)

        left_cols = self.scope.joined_left_cols[join]
        right_cols = self.scope.tables.get_columns(table.alias_or_name)

        kind = join.method or join.kind
        using: list[Identifier] | None = join.args.get('using')
        condition = join.args.get('on')

        if using or kind == 'NATURAL':
            shared_columns = list(set(left_cols) & set(right_cols))
            join_columns = [ident.name for ident in using] if using else shared_columns
            self._validate_join_columns(join_columns, left_cols, right_cols, join)

        elif kind == 'CROSS':
            # CROSS JOINS must not have a condition
            if condition:
                raise InvalidJoinConditionError(condition)
        else:
            # INNER, LEFT, RIGHT, and FULL OUTER joins must have a condition
            if not condition:
                raise MissingJoinConditionError(join)
            self.expr_validator.validate_boolean(condition)

    def _validate_join_columns(
        self, join_columns: list[str], left: Attributes, right: Attributes, join: Join
    ) -> None:
        for col in join_columns:
            if col not in left:
                raise ColumnNotFoundError.from_expression(join, col)
            assert_comparable(left[col], right[col], join)
