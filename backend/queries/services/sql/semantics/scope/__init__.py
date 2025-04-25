from __future__ import annotations

from databases.types import DataType
from sqlglot.expressions import Column

from ..context import ValidationContext
from .group_by import GroupByScope
from .projections import ProjectionsScope
from .tables import TablesScope


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.tables: TablesScope = TablesScope(parent.tables if parent else None)
        self.projections = ProjectionsScope()
        self.group_by = GroupByScope()

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by._exprs)

    def resolve_column(self, column: Column, context: ValidationContext) -> DataType:
        if context.in_order_by and (t := self.projections.resolve(column)):
            return t
        return self.tables.resolve_column(column)
