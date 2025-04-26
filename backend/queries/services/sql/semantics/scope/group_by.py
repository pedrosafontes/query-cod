from __future__ import annotations

from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Expression


class GroupByScope:
    def __init__(self) -> None:
        self._exprs: list[tuple[Expression, DataType]] = []

    def add(self, expr: Expression, t: DataType) -> None:
        self._exprs.append((expr, t))

    def contains(self, expr: Expression) -> bool:
        return self._get(expr) is not None

    def type_of(self, expr: Expression) -> DataType | None:
        return self._get(expr)

    def _get(self, expr: Expression) -> DataType | None:
        for grouped, t in self._exprs:
            if expr == grouped or expr.name == grouped.name:
                return t
        return None
