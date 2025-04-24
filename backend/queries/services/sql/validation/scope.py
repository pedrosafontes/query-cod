from __future__ import annotations

from collections import defaultdict

from databases.types import DataType, TableSchema
from sqlglot import Expression
from sqlglot.expressions import Column

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
ColumnBindings = dict[ColumnName, list[DataType]]


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.parent = parent
        self._table_schemas: ResultSchema = defaultdict(dict)
        self.group_by: set[str] = set()
        self.projection_schema: ResultSchema = defaultdict(dict)

    def register_table(self, alias: str, schema: TableSchema) -> None:
        if alias in self._table_schemas:
            raise DuplicateAliasError(alias)
        self._table_schemas[alias] = schema

    def add_select_item(self, table: str | None, alias: str, t: DataType) -> None:
        if alias in self.projection_schema[table]:
            raise DuplicateAliasError(alias)
        self.projection_schema[table][alias] = t

    def get_columns(self) -> set[str]:
        columns: list[str] = []
        for _, schema in self._table_schemas.items():
            columns.extend(schema.keys())
        return set(columns)

    def get_schema(self) -> ResultSchema:
        return self._table_schemas

    def get_table_schema(self, alias: str) -> ResultSchema:
        if alias not in self._table_schemas:
            raise UndefinedTableError(alias)

        return {alias: self._table_schemas[alias]}

    def resolve_column(self, column: Column) -> DataType:
        name = column.name
        table = column.table

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
        matches: list[tuple[TableAlias | None, DataType]] = []
        for table, schema in self._table_schemas.items():
            if name in schema:
                matches.append((table, schema[name]))
        if not matches:
            raise UndefinedColumnError(name)
        if len(matches) != 1:
            tables = [table for table, _ in matches if table]
            raise AmbiguousColumnError(name, tables)
        [(_, t)] = matches
        return t

    def resolve_projection(self, expr: Expression) -> bool:
        name = expr.name
        table = expr.table if isinstance(expr, Column) else None

        if table:
            return self._resolve_qualified_projection(name, table)
        else:
            return self._resolve_unqualified_projection(name)

    def _resolve_qualified_projection(self, name: str, table: str) -> bool:
        return table in self.projection_schema and name in self.projection_schema[table]

    def _resolve_unqualified_projection(self, name: str) -> bool:
        matches = []
        for table, schema in self.projection_schema.items():
            if name in schema:
                matches.append(table)
        if len(matches) == 1:
            return True
        return False

    def snapshot_columns(self) -> ColumnBindings:
        column_types = defaultdict(list)
        for _, schema in self._table_schemas.items():
            for col, t in schema.items():
                column_types[col].append(t)
        return column_types
