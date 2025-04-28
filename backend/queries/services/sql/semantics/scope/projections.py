from __future__ import annotations

from collections import defaultdict

from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Column, Expression

from ..errors import (
    DuplicateAliasError,
)


class ProjectionsScope:
    def __init__(self) -> None:
        self.schema: RelationalSchema = defaultdict(dict)  # Track projections by alias
        self.expressions: dict[Expression, DataType] = {}  # Track projections by expression

    @property
    def types(self) -> list[DataType]:
        return list(self.expressions.values())

    def add(self, expr: Expression, t: DataType) -> None:
        # Add to expressions
        self.expressions[expr] = t

        # Add to schema
        alias = expr.alias_or_name
        table = expr.args.get('table')
        # Check for duplicate alias
        if alias and alias in self.schema[table]:
            raise DuplicateAliasError(alias)
        self.schema[table][alias] = t

    def contains(self, expr: Expression) -> bool:
        return self.resolve(expr) is not None

    def resolve(self, expr: Expression) -> DataType | None:
        if expr in self.expressions:
            # Exact match
            return self.expressions[expr]

        # Resolve by alias
        name = expr.alias_or_name
        table = expr.table if isinstance(expr, Column) else None
        return self._resolve_qualified(name, table) if table else self._resolve_unqualified(name)

    def _resolve_qualified(self, name: str, table: str) -> DataType | None:
        return self.schema[table].get(name)

    def _resolve_unqualified(self, name: str) -> DataType | None:
        matches = [schema[name] for schema in self.schema.values() if name in schema]
        return matches[0] if matches else None
