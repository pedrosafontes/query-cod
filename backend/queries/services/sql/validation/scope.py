from __future__ import annotations

from collections import defaultdict

from databases.types import DataType, TableSchema
from sqlglot.expressions import Column

from .errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    UndefinedColumnError,
    UndefinedTableError,
)


ColumnBinding = tuple[str, DataType]
ColumnBindings = dict[str, list[ColumnBinding]]


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.parent = parent
        self._aliases: dict[str, str] = {}
        self._columns: ColumnBindings = defaultdict(list)
        self.group_by: set[str] = set()
        self.projection_schema: TableSchema = {}

    def register_table(self, alias: str, table: str, schema: dict[str, DataType]) -> None:
        if alias in self._aliases:
            raise DuplicateAliasError(alias)
        self._aliases[alias] = table
        for col, dtype in schema.items():
            self._columns[col.lower()].append((alias, dtype))

    def add_select_item(self, alias: str, t: DataType) -> None:
        if alias in self.projection_schema:
            raise DuplicateAliasError(alias)
        self.projection_schema[alias] = t

    def get_column_bindings(self, col: str) -> list[ColumnBinding]:
        return self._columns.get(col.lower(), [])

    def get_columns(self) -> set[str]:
        return set(self._columns.keys())

    def get_schema(self) -> TableSchema:
        return {col: self._infer_type(types) for col, types in self._columns.items()}

    def _infer_type(self, types: list[ColumnBinding]) -> DataType:
        return types[0][1]

    def resolve_column(self, column: Column) -> DataType:
        name = column.name.lower()
        alias = column.table

        if alias:
            return self._resolve_qualified(name, alias)
        return self._resolve_unqualified(name)

    def _resolve_qualified(self, name: str, alias: str) -> DataType:
        if alias not in self._aliases:
            if self.parent:
                return self.parent._resolve_qualified(name, alias)
            raise UndefinedTableError(alias)
        for col_alias, dtype in self._columns.get(name, []):
            if col_alias == alias:
                return dtype
        raise UndefinedColumnError(name, self._aliases[alias])

    def _resolve_unqualified(self, name: str) -> DataType:
        entries = self._columns.get(name, [])
        if not entries:
            if self.parent:
                return self.parent._resolve_unqualified(name)
            raise UndefinedColumnError(name)
        if len(entries) > 1:
            raise AmbiguousColumnError(name, [a for a, _ in entries])
        return entries[0][1]

    def snapshot_columns(self) -> ColumnBindings:
        # Deep copy to isolate subsequent mutations
        return defaultdict(list, {k: v.copy() for k, v in self._columns.items()})
