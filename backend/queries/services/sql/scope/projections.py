from __future__ import annotations

from collections import defaultdict

from queries.services.types import RelationalSchema, flatten
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Expression


class ProjectionsScope:
    def __init__(self) -> None:
        self.schema: RelationalSchema = defaultdict(dict)  # Track projections by alias
        self.expressions: list[Expression] = []  # Track projections by expression

    @property
    def types(self) -> list[DataType]:
        return list(flatten(self.schema).values())

    def add(self, expr: Expression, t: DataType) -> None:
        # Add to expressions
        self.expressions.append(expr)

        # Add to schema
        alias = expr.alias_or_name
        table = expr.args.get('table')
        self.schema[table][alias] = t

    def __contains__(self, expr: Expression) -> bool:
        return any(
            expr == projection or expr.alias_or_name == projection.alias_or_name
            for projection in self.expressions
        )
