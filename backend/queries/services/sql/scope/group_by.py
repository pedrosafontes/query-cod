from __future__ import annotations

from sqlglot.expressions import Expression


class GroupByScope:
    def __init__(self, exprs: list[Expression]) -> None:
        self.exprs = exprs

    def contains(self, expr: Expression) -> bool:
        return any(expr == grouped or expr.name == grouped.name for grouped in self.exprs)
