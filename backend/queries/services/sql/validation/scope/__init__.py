from __future__ import annotations

from databases.types import DataType
from sqlglot.expressions import Column

from ..errors import NonGroupedColumnError
from ..types import ResultSchema
from .group_by_scope import GroupByScope
from .projection_scope import ProjectionScope
from .table_scope import TableScope


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.tables: TableScope = TableScope(parent.tables if parent else None)
        self.projections = ProjectionScope()
        self.group_by = GroupByScope()

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by._group_by_exprs)

    def validate_star_expansion(self, table: str | None = None) -> ResultSchema:
        schema = self.tables.get_table_schema(table) if table else self.tables.get_schema()

        if self.is_grouped:
            missing: list[str] = []
            for table, table_schema in schema.items():
                for col, _ in table_schema.items():
                    col_expr = Column(this=col, table=table)
                    if not self.group_by.contains(col_expr):
                        missing.append(col)

            if missing:
                raise NonGroupedColumnError(missing)

        return schema

    def resolve_column(self, column: Column, in_order_by: bool = False) -> DataType:
        if in_order_by and (t := self.projections.resolve(column)):
            return t
        return self.tables.resolve_column(column)
