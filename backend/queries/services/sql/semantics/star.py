from sqlglot.expressions import Column, Star

from ..scope import SelectScope
from .errors import UngroupedColumnError


class StarValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def validate(self, expr: Star | Column) -> None:
        if not self.scope.is_grouped:
            return

        # Find columns expanded from star that are not in the GROUP BY
        missing = [
            col.name
            for col in self.scope.expand_star(expr)
            if not self.scope.group_by.contains(col)
        ]

        if missing:
            raise UngroupedColumnError(expr, missing)
