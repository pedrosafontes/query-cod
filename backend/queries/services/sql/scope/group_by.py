from __future__ import annotations

from sqlglot.expressions import Expression


class GroupByExpressions:
    def __init__(self, exprs: list[Expression]) -> None:
        self.exprs = exprs

    def __contains__(self, expr: Expression) -> bool:
        return any(expr == grouped or expr.name == grouped.name for grouped in self.exprs)
