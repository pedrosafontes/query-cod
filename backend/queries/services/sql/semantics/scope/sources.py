from __future__ import annotations

from collections import defaultdict

from databases.types import DataType, TableSchema
from sqlglot.expressions import Column

from ..errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    UndefinedColumnError,
    UndefinedTableError,
)
from ..types import ColumnTypes, ResultSchema


class SourcesScope:
    def __init__(self, parent: SourcesScope | None = None) -> None:
        self.parent = parent
        self._table_schemas: ResultSchema = defaultdict(dict)

    def add(self, alias: str, schema: TableSchema) -> None:
        # Check for duplicate alias
        if alias in self._table_schemas:
            raise DuplicateAliasError(alias)
        self._table_schemas[alias] = schema

    def resolve_column(self, column: Column, in_order_by: bool = False) -> DataType:
        name = column.name
        table = column.table
        return self._resolve_qualified(name, table) if table else self._resolve_unqualified(name)

    def _resolve_qualified(self, name: str, table: str) -> DataType:
        if table not in self._table_schemas:
            # Check if the table is in the parent scope
            if self.parent:
                return self.parent._resolve_qualified(name, table)
            raise UndefinedTableError(table)
        # Table is in the current scope
        if name not in self._table_schemas[table]:
            raise UndefinedColumnError(name, table)
        return self._table_schemas[table][name]

    def _resolve_unqualified(self, name: str) -> DataType:
        matches = [
            (table, schema[name]) for table, schema in self._table_schemas.items() if name in schema
        ]
        if not matches:
            # Check if the column is in the parent scope
            if self.parent:
                return self.parent._resolve_unqualified(name)
            raise UndefinedColumnError(name)
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousColumnError(name, [table for table, _ in matches if table])
        # There is only one match
        [(_, t)] = matches
        return t

    # ────── Utilities ──────

    def get_schema(self) -> ResultSchema:
        return self._table_schemas

    def get_table_schema(self, table: str) -> ResultSchema:
        if table not in self._table_schemas:
            raise UndefinedTableError(table)
        return {table: self._table_schemas[table]}

    def snapshot_columns(self) -> ColumnTypes:
        column_types = defaultdict(list)
        for schema in self._table_schemas.values():
            for col, t in schema.items():
                column_types[col].append(t)
        return column_types
