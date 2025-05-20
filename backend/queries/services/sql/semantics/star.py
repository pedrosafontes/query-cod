from sqlglot.expressions import Column, Star

from ..scope import SelectScope
from .errors import RelationNotFoundError, UngroupedColumnError


class StarValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def validate(self, expr: Star | Column) -> None:
        if not self.scope.is_grouped:
            return

        expanded_cols = self.scope.expand_star(expr)
        if expanded_cols is None:
            raise RelationNotFoundError(expr)

        # Find columns expanded from star that are not in the GROUP BY
        missing = [col.name for col in expanded_cols if not self.scope.group_by.contains(col)]

        if missing:
            raise UngroupedColumnError(expr, missing)
