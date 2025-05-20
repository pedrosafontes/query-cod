from __future__ import annotations

import copy
from collections import defaultdict

from queries.services.types import Attributes, RelationalSchema, merge_common_column
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Column, Expression, Subquery, Table

from ..semantics.errors import (
    AmbiguousColumnReferenceError,
)


class TablesScope:
    def __init__(self, parent: TablesScope | None = None) -> None:
        self.parent = parent
        self._schema: RelationalSchema = defaultdict(dict)
        self._tables: list[Table | Subquery] = []

    def add(self, table: Table | Subquery, attributes: Attributes) -> None:
        self._tables.append(table)
        self._schema[table.alias_or_name] = attributes

    def resolve_column(self, column: Column, validate: bool = True) -> DataType | None:
        return (
            self._resolve_qualified(column)
            if column.table
            else self._resolve_unqualified(column, validate)
        )

    def _resolve_qualified(self, column: Column) -> DataType | None:
        if column.table not in self._schema:
            # Check if the table is in the parent scope
            return self.parent._resolve_qualified(column) if self.parent else None
        # Table is in the current scope
        return self._schema[column.table].get(column.name)

    def _resolve_unqualified(self, column: Column, validate: bool) -> DataType | None:
        matches = [
            (table, attributes[column.name])
            for table, attributes in self._schema.items()
            if column.name in attributes
        ]

        if not matches:
            # Check if the column is in the parent scope
            return self.parent._resolve_unqualified(column, validate) if self.parent else None

        # Check for ambiguous column
        if len(matches) > 1:
            if validate:
                raise AmbiguousColumnReferenceError(
                    column, [table for table, _ in matches if table]
                )
            else:
                return None
        
        # There is only one match
        [(_, t)] = matches
        return t

    def merge_common_column(self, col: str) -> None:
        merge_common_column(self._schema, col)

    # ────── Utilities ──────

    def get_schema(self) -> RelationalSchema:
        return copy.deepcopy(self._schema)

    def get_table_schema(self, table: str) -> RelationalSchema | None:
        if table not in self._schema:
            return None
        return {table: self._schema[table].copy()}

    def get_columns(self) -> Attributes:
        # Get all column types from all tables
        all_column_types = defaultdict(list)
        for attributes in self._schema.values():
            for col, t in attributes.items():
                all_column_types[col].append(t)
        # Get the dominant type for each column
        column_types = {}
        for col, types in all_column_types.items():
            column_types[col] = DataType.dominant(types)

        return column_types
