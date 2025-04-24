from __future__ import annotations

from collections import defaultdict

from databases.types import DataType, TableSchema
from sqlglot.expressions import Column, Expression

from .errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    UndefinedColumnError,
    UndefinedTableError,
)


TableAlias = str
ColumnName = str
ProjectionSchema = dict[ColumnName, DataType]
ResultSchema = dict[TableAlias | None, ProjectionSchema]
ColumnTypes = dict[ColumnName, list[DataType]]


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.parent = parent
        self._table_schemas: ResultSchema = defaultdict(dict)
        self.group_by: set[str] = set()
        self.projection_schema: ResultSchema = defaultdict(dict)

    # ────── Table Registration ──────

    def register_table(self, alias: str, schema: TableSchema) -> None:
        if alias in self._table_schemas:
            raise DuplicateAliasError(alias)
        self._table_schemas[alias] = schema

    # ────── Projection Registration ──────

    def add_select_item(self, table: str | None, alias: str, t: DataType) -> None:
        if alias in self.projection_schema[table]:
            raise DuplicateAliasError(alias)
        self.projection_schema[table][alias] = t

    def is_projected(self, expr: Expression) -> bool:
        return self._resolve_projection(expr) is not None

    def _resolve_projection(self, expr: Expression) -> DataType | None:
        name = expr.name
        table = expr.table if isinstance(expr, Column) else None

        if table:
            return self._resolve_qualified_projection(name, table)
        return self._resolve_unqualified_projection(name)

    def _resolve_qualified_projection(self, name: str, table: str) -> DataType | None:
        return self.projection_schema[table].get(name)

    def _resolve_unqualified_projection(self, name: str) -> DataType | None:
        matches = self._find_projection_matches(name)
        return matches[0] if matches else None

    def _find_projection_matches(self, name: str) -> list[DataType]:
        return [schema[name] for schema in self.projection_schema.values() if name in schema]

    # ────── Column Resolution ──────

    def resolve_column(self, column: Column, in_order_by: bool = False) -> DataType:
        name = column.name
        table = column.table
        if in_order_by and (t := self._resolve_projection(column)):
            return t
        if table:
            return self._resolve_qualified(name, table)
        return self._resolve_unqualified(name)

    def _resolve_qualified(self, name: str, table: str) -> DataType:
        if table not in self._table_schemas:
            if self.parent:
                return self.parent._resolve_qualified(name, table)
            raise UndefinedTableError(table)
        if name not in self._table_schemas[table]:
            raise UndefinedColumnError(name, table)
        return self._table_schemas[table][name]

    def _resolve_unqualified(self, name: str) -> DataType:
        matches = [
            (table, schema[name]) for table, schema in self._table_schemas.items() if name in schema
        ]
        if not matches:
            if self.parent:
                return self.parent._resolve_unqualified(name)
            raise UndefinedColumnError(name)
        if len(matches) > 1:
            raise AmbiguousColumnError(name, [table for table, _ in matches if table])
        [(_, t)] = matches
        return t

    def get_column_type(self, name: str, table: str | None = None) -> DataType:
        return self._resolve_qualified(name, table) if table else self._resolve_unqualified(name)

    # ────── Schema Utilities ──────

    def get_columns(self) -> set[str]:
        return set([col for schema in self._table_schemas.values() for col in schema.keys()])

    def get_schema(self) -> ResultSchema:
        return self._table_schemas

    def get_table_schema(self, table: str) -> ResultSchema:
        if table not in self._table_schemas:
            raise UndefinedTableError(table)
        return {table: self._table_schemas[table]}

    def snapshot_columns(self) -> ColumnTypes:
        column_types = defaultdict(list)
        for _, schema in self._table_schemas.items():
            for col, t in schema.items():
                column_types[col].append(t)
        return column_types
