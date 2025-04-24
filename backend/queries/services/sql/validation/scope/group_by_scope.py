from __future__ import annotations

from databases.types import DataType
from sqlglot.expressions import Expression


class GroupByScope:
    def __init__(self) -> None:
        self._group_by_exprs: list[tuple[Expression, DataType]] = []

    def add_expr(self, expr: Expression, t: DataType) -> None:
        self._group_by_exprs.append((expr, t))

    def contains(self, expr: Expression) -> bool:
        return self._get_expr(expr) is not None

    def type_of(self, expr: Expression) -> DataType | None:
        match = self._get_expr(expr)
        return match[1] if match else None

    def _get_expr(self, expr: Expression) -> tuple[Expression, DataType] | None:
        for grouped, t in self._group_by_exprs:
            if expr == grouped or expr.name == grouped.name:
                return grouped, t
        return None
