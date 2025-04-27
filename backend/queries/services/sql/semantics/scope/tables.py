from __future__ import annotations

from collections import defaultdict

from databases.types import TableSchema
from queries.services.types import ResultSchema, merge_common_column
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Column

from ..errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    UndefinedTableError,
)


class TablesScope:
    def __init__(self, parent: TablesScope | None = None) -> None:
        self.parent = parent
        self._table_schemas: ResultSchema = defaultdict(dict)

    def add(self, alias: str, schema: TableSchema) -> None:
        # Check for duplicate alias
        if alias in self._table_schemas:
            raise DuplicateAliasError(alias)
        self._table_schemas[alias] = schema

    def resolve_column(self, column: Column) -> DataType | None:
        name = column.name
        table = column.table
        return self._resolve_qualified(name, table) if table else self._resolve_unqualified(name)

    def _resolve_qualified(self, name: str, table: str) -> DataType | None:
        if table not in self._table_schemas:
            # Check if the table is in the parent scope
            return self.parent._resolve_qualified(name, table) if self.parent else None
        # Table is in the current scope
        return self._table_schemas[table].get(name)

    def _resolve_unqualified(self, name: str) -> DataType | None:
        matches = [
            (table, schema[name]) for table, schema in self._table_schemas.items() if name in schema
        ]
        if not matches:
            # Check if the column is in the parent scope
            return self.parent._resolve_unqualified(name) if self.parent else None
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousColumnError(name, [table for table, _ in matches if table])
        # There is only one match
        [(_, t)] = matches
        return t

    def merge_common_column(self, col: str) -> None:
        merge_common_column(self._table_schemas, col)

    # ────── Utilities ──────

    def get_schema(self) -> ResultSchema:
        return self._table_schemas

    def get_table_schema(self, table: str) -> ResultSchema:
        if table not in self._table_schemas:
            raise UndefinedTableError(table)
        return {table: self._table_schemas[table]}

    def get_columns(self) -> TableSchema:
        # Get all column types from all tables
        all_column_types = defaultdict(list)
        for schema in self._table_schemas.values():
            for col, t in schema.items():
                all_column_types[col].append(t)
        # Get the dominant type for each column
        column_types = {}
        for col, types in all_column_types.items():
            column_types[col] = DataType.dominant(types)

        return column_types
