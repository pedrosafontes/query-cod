from __future__ import annotations

from collections import defaultdict

from databases.types import ColumnSchema
from queries.services.types import RelationalSchema, merge_common_column
from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import Column, Subquery, Table

from ..errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    UndefinedTableError,
)


class TablesScope:
    def __init__(self, parent: TablesScope | None = None) -> None:
        self.parent = parent
        self._table_schemas: RelationalSchema = defaultdict(dict)

    def add(self, table: Table | Subquery, schema: ColumnSchema) -> None:
        alias = table.alias_or_name
        # Check for duplicate alias
        if alias in self._table_schemas:
            raise DuplicateAliasError(table)
        self._table_schemas[alias] = schema

    def resolve_column(self, column: Column) -> DataType | None:
        return (
            self._resolve_qualified(column) if column.table else self._resolve_unqualified(column)
        )

    def _resolve_qualified(self, column: Column) -> DataType | None:
        if column.table not in self._table_schemas:
            # Check if the table is in the parent scope
            return self.parent._resolve_qualified(column) if self.parent else None
        # Table is in the current scope
        return self._table_schemas[column.table].get(column.name)

    def _resolve_unqualified(self, column: Column) -> DataType | None:
        matches = [
            (table, schema[column.name])
            for table, schema in self._table_schemas.items()
            if column.name in schema
        ]
        if not matches:
            # Check if the column is in the parent scope
            return self.parent._resolve_unqualified(column) if self.parent else None
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousColumnError(column, [table for table, _ in matches if table])
        # There is only one match
        [(_, t)] = matches
        return t

    def merge_common_column(self, col: str) -> None:
        merge_common_column(self._table_schemas, col)

    # ────── Utilities ──────

    def get_schema(self) -> RelationalSchema:
        return self._table_schemas

    def get_table_schema(self, table: str, source: Expression) -> RelationalSchema:
        if table not in self._table_schemas:
            raise UndefinedTableError(source, table)
        return {table: self._table_schemas[table]}

    def get_columns(self) -> ColumnSchema:
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
