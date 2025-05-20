from sqlglot.expressions import Column, Star

from ..scope import SelectScope
from .errors import UngroupedColumnError


class StarValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def validate(self, expr: Star | Column) -> None:
        if self.scope.is_grouped:
            missing: list[str] = []
            for col in self.scope.expand_star(expr):
                if not self.scope.group_by.contains(col):
                    missing.append(col.name)

            if missing:
                raise UngroupedColumnError(expr, missing)
