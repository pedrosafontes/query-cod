from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from queries.services.types import (
    Attributes,
    RelationalSchema,
    flatten,
    merge_common_column,
)
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Column, Join, table_

from ..semantics.errors import (
    AmbiguousColumnReferenceError,
)
from ..types import SQLTable


if TYPE_CHECKING:
    from .query import DerivedTableScope, SelectScope


@dataclass
class Source:
    table: SQLTable
    joins: list[Join]
    attributes: Attributes


class TablesScope:
    def __init__(self, select_scope: SelectScope, parent: TablesScope | None = None) -> None:
        self.select_scope = select_scope
        self.parent = parent
        self._joined_schema: RelationalSchema = {}
        self._tables_schemas: RelationalSchema = {}
        self.derived_table_scopes: dict[str, DerivedTableScope] = {}

    def add(self, table: SQLTable, attributes: Attributes) -> None:
        name = table.alias_or_name
        self._tables_schemas[name] = attributes.copy()
        self._joined_schema[name] = attributes.copy()

    def resolve_column(self, column: Column, validate: bool = True) -> DataType | None:
        result = self.find_col(column, validate)
        return result[1] if result else None

    def find_col(self, column: Column, validate: bool = True) -> tuple[Source, DataType] | None:
        return (
            self._find_qualified(column)
            if column.table
            else self._find_unqualified(column, validate)
        )

    def _find_qualified(self, column: Column) -> tuple[Source, DataType] | None:
        table = column.table
        if (
            table in self._tables_schemas
            and table in self._joined_schema
            and column.name in self._joined_schema[table]
        ):
            # Table is in the current scope
            return (
                self._get_source(table),
                self._joined_schema[table][column.name],
            )
        else:
            # Check if the table is in the parent scope
            return self.parent._find_qualified(column) if self.parent else None

    def _find_unqualified(self, column: Column, validate: bool) -> tuple[Source, DataType] | None:
        tables = [
            table for table, attributes in self._joined_schema.items() if column.name in attributes
        ]

        if not tables:
            # Check if the column is in the parent scope
            return self.parent._find_unqualified(column, validate) if self.parent else None

        # Check for ambiguous column
        if len(tables) > 1:
            if validate:
                raise AmbiguousColumnReferenceError(column, [t for t in tables if t])
            else:
                return None

        # There is only one match
        [table] = tables

        return (
            self._get_source(table),
            self._joined_schema[table][column.name],
        )

    def merge_column(self, col: str) -> None:
        merge_common_column(self._joined_schema, col)

    def get_schema(self) -> RelationalSchema:
        return copy.deepcopy(self._joined_schema)

    def get_all_columns(self) -> Attributes:
        return flatten(self.get_schema())

    def find_columns(self, table: str) -> Attributes | None:
        if table not in self._tables_schemas:
            return None
        return self._tables_schemas[table].copy()

    def get_columns(self, table: str) -> Attributes:
        return cast(Attributes, self.find_columns(table))

    def _get_source(self, table_name: str | None) -> Source:
        if table_name:
            return Source(
                table=self.derived_table_scopes[table_name].query
                if table_name in self.derived_table_scopes
                else table_(table_name),
                joins=[],
                attributes=self.get_columns(table_name),
            )
        else:
            return Source(
                table=cast(SQLTable, self.select_scope.from_),
                joins=self.select_scope.joins,
                attributes=self.get_all_columns(),
            )
