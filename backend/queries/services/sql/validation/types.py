from __future__ import annotations

from collections import defaultdict

from databases.types import DataType
from sqlglot.expressions import Column

from .errors import AmbiguousColumnError, UndefinedColumnError, UndefinedTableError


class Scope:
    def __init__(self, parent: Scope | None = None) -> None:
        self.parent: Scope | None = parent
        self.tables: dict[str, str] = {}  # table alias → table name
        self.columns: dict[str, list[tuple[str, DataType]]] = defaultdict(
            list
        )  # column name → list[(table alias, dtype)]
        self.group_by_cols: set[str] = set()

    def add_column(self, table: str, column: str, dtype: DataType) -> None:
        entry = (table, dtype)
        if entry not in self.columns[column.lower()]:
            self.columns[column.lower()].append(entry)

    def resolve_column(self, column: Column) -> DataType:
        table_or_alias = column.table

        # Qualified
        if table_or_alias:
            if table_or_alias not in self.tables:
                if self.parent:
                    return self.parent.resolve_column(column)
                else:
                    raise UndefinedTableError(table_or_alias)

            table = self.tables[table_or_alias]
            for alias, dtype in self.columns.get(column.name, []):
                if alias == table_or_alias:
                    return dtype
            raise UndefinedColumnError(column.name, table)

        # Unqualified
        candidates = self.columns.get(column.name, [])
        if not candidates:
            if self.parent:
                return self.parent.resolve_column(column)
            else:
                raise UndefinedColumnError(column.name)
        if len(candidates) > 1:
            raise AmbiguousColumnError(column.name, [a for a, _ in candidates])
        _, dtype = candidates[0]
        return dtype
