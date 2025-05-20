from __future__ import annotations

import copy
from collections import defaultdict

from queries.services.types import Attributes, RelationalSchema, merge_common_column
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Column, Subquery, Table

from ..semantics.errors import (
    AmbiguousColumnReferenceError,
)


class TablesScope:
    def __init__(self, parent: TablesScope | None = None) -> None:
        self.parent = parent
        self._schema: RelationalSchema = defaultdict(dict)
        self._tables_schemas: RelationalSchema = defaultdict(dict)

    def add(self, table: Table | Subquery, attributes: Attributes) -> None:
        name = table.alias_or_name
        self._tables_schemas[name] = attributes.copy()
        self._schema[name] = attributes.copy()

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

    def merge_column(self, col: str) -> None:
        merge_common_column(self._schema, col)

    def get_schema(self) -> RelationalSchema:
        return copy.deepcopy(self._schema)

    def get_table_schema(self, table: str) -> RelationalSchema | None:
        if table not in self._tables_schemas:
            return None
        return {table: self._tables_schemas[table].copy()}
