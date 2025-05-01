from __future__ import annotations

from collections import defaultdict

from queries.services.types import Attributes, RelationalSchema, merge_common_column
from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import Column, Subquery, Table

from ..errors import (
    AmbiguousColumnReferenceError,
    DuplicateAliasError,
    RelationNotFoundError,
)


class TablesScope:
    def __init__(self, parent: TablesScope | None = None) -> None:
        self.parent = parent
        self._tables: RelationalSchema = defaultdict(dict)

    def add(self, table: Table | Subquery, attributes: Attributes) -> None:
        alias = table.alias_or_name
        # Check for duplicate alias
        if alias in self._tables:
            raise DuplicateAliasError(table)
        self._tables[alias] = attributes

    def resolve_column(self, column: Column) -> DataType | None:
        return (
            self._resolve_qualified(column) if column.table else self._resolve_unqualified(column)
        )

    def _resolve_qualified(self, column: Column) -> DataType | None:
        if column.table not in self._tables:
            # Check if the table is in the parent scope
            return self.parent._resolve_qualified(column) if self.parent else None
        # Table is in the current scope
        return self._tables[column.table].get(column.name)

    def _resolve_unqualified(self, column: Column) -> DataType | None:
        matches = [
            (table, attributes[column.name])
            for table, attributes in self._tables.items()
            if column.name in attributes
        ]
        if not matches:
            # Check if the column is in the parent scope
            return self.parent._resolve_unqualified(column) if self.parent else None
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousColumnReferenceError(column, [table for table, _ in matches if table])
        # There is only one match
        [(_, t)] = matches
        return t

    def merge_common_column(self, col: str) -> None:
        merge_common_column(self._tables, col)

    # ────── Utilities ──────

    def get_schema(self) -> RelationalSchema:
        return self._tables

    def get_table_schema(self, table: str, source: Expression) -> RelationalSchema:
        if table not in self._tables:
            raise RelationNotFoundError(source, table)
        return {table: self._tables[table]}

    def get_columns(self) -> Attributes:
        # Get all column types from all tables
        all_column_types = defaultdict(list)
        for attributes in self._tables.values():
            for col, t in attributes.items():
                all_column_types[col].append(t)
        # Get the dominant type for each column
        column_types = {}
        for col, types in all_column_types.items():
            column_types[col] = DataType.dominant(types)

        return column_types
