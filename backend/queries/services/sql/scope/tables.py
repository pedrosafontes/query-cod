from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, cast

from queries.services.types import (
    Attributes,
    RelationalSchema,
    flatten,
    merge_common_column,
)
from query_cod.types import DataType
from sqlglot.expressions import Column, Table, select, table_

from ..semantics.errors import (
    AmbiguousColumnReferenceError,
)
from ..types import SQLTable


if TYPE_CHECKING:
    from .query import DerivedTableScope, SelectScope, SQLScope


@dataclass
class Source:
    table: Table | SQLScope
    name: str | None
    attributes: Attributes


class TablesScope:
    def __init__(self, select_scope: SelectScope, parent: TablesScope | None = None) -> None:
        self.select_scope = select_scope
        self.parent = parent
        self._joined_schema: RelationalSchema = {}
        self._tables_schemas: RelationalSchema = {}
        self.derived_table_scopes: dict[str, DerivedTableScope] = {}
        self._aliases: dict[str, str] = {}

    def add(self, table: SQLTable, attributes: Attributes) -> None:
        if table.alias:
            self._aliases[table.alias] = table.name

        name = table.alias_or_name
        self._tables_schemas[name] = attributes.copy()
        self._joined_schema[name] = attributes.copy()

    def __contains__(self, column: Column) -> bool:
        if column.table:
            return (
                column.table in self._joined_schema
                and column.name in self._joined_schema[column.table]
            )
        else:
            return any(column.name in attributes for attributes in self._joined_schema.values())

    def find_column_type(self, column: Column) -> DataType | None:
        return self._resolve_column(
            column, lambda scope, table, column: scope._joined_schema[table][column.name]
        )

    def find_column_source(self, column: Column) -> Source | None:
        return self._resolve_column(column, lambda scope, table, column: scope._get_source(table))

    def can_resolve(self, column: Column) -> bool:
        return (
            self._resolve_column(column, lambda scope, table, column: True, validate=True)
            is not None
        )

    T = TypeVar('T')

    def _resolve_column(
        self,
        column: Column,
        func: Callable[[TablesScope, str | None, Column], T],
        validate: bool = True,
    ) -> T | None:
        return (
            self._resolve_qualified(column, func)
            if column.table
            else self._resolve_unqualified(column, func, validate)
        )

    def _resolve_qualified(
        self, column: Column, func: Callable[[TablesScope, str | None, Column], T]
    ) -> T | None:
        if column in self:
            # Column is in the current scope
            table = column.table
            return func(self, table, column)
        else:
            # Check if the table is in the parent scope
            return self.parent._resolve_qualified(column, func) if self.parent else None

    def _resolve_unqualified(
        self, column: Column, func: Callable[[TablesScope, str | None, Column], T], validate: bool
    ) -> T | None:
        tables = [
            table for table, attributes in self._joined_schema.items() if column.name in attributes
        ]

        if not tables:
            # Check if the column is in the parent scope
            return self.parent._resolve_unqualified(column, func, validate) if self.parent else None

        # Check for ambiguous column
        if len(tables) > 1:
            if validate:
                raise AmbiguousColumnReferenceError(column, [t for t in tables if t])
            else:
                return None

        # There is only one match
        [table] = tables

        return func(self, table, column)

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

    def _get_source(self, name_or_alias: str | None) -> Source:
        from ..scope.builder import build_scope

        if name_or_alias:
            aliased = self._aliases.get(name_or_alias)
            name = aliased or name_or_alias
            alias = name_or_alias if aliased else None
            return Source(
                table=self.derived_table_scopes[name_or_alias]
                if name_or_alias in self.derived_table_scopes
                else table_(table=name, alias=alias),
                name=name_or_alias,
                attributes=self.get_schema()[name_or_alias],
            )
        else:
            assert self.select_scope.from_ is not None  # noqa: S101

            query = select('*').from_(self.select_scope.from_.this)
            query.set('joins', self.select_scope.joins)
            return Source(
                table=build_scope(
                    query,
                    self.select_scope.db_schema,
                ),
                name=None,
                attributes=self.get_all_columns(),
            )
