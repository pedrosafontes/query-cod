from __future__ import annotations

from collections import defaultdict

from databases.types import DataType, TableSchema
from sqlglot.expressions import Column, Expression

from .errors import (
    AmbiguousColumnError,
    DuplicateAliasError,
    NonGroupedColumnError,
    UndefinedColumnError,
    UndefinedTableError,
)


TableAlias = str
ColumnName = str
ProjectionSchema = dict[ColumnName, DataType]
ResultSchema = dict[TableAlias | None, ProjectionSchema]
ColumnTypes = dict[ColumnName, list[DataType]]


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.parent = parent
        self._table_schemas: ResultSchema = defaultdict(dict)
        self._group_by_exprs: list[tuple[Expression, DataType]] = []
        self.projection_schema: ResultSchema = defaultdict(dict)

    # ────── Table & Column Resolution ──────

    def register_table(self, alias: str, schema: TableSchema) -> None:
        if alias in self._table_schemas:
            raise DuplicateAliasError(alias)
        self._table_schemas[alias] = schema

    def resolve_column(self, column: Column, in_order_by: bool = False) -> DataType:
        name = column.name
        table = column.table
        if in_order_by and (t := self._resolve_projection(column)):
            return t
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
        matches = [
            (table, schema[name]) for table, schema in self._table_schemas.items() if name in schema
        ]
        if not matches:
            if self.parent:
                return self.parent._resolve_unqualified(name)
            raise UndefinedColumnError(name)
        if len(matches) > 1:
            raise AmbiguousColumnError(name, [table for table, _ in matches if table])
        [(_, t)] = matches
        return t

    # ────── Projection Resolution ──────

    def add_projection(self, table: str | None, alias: str, t: DataType) -> None:
        if alias and alias in self.projection_schema[table]:
            raise DuplicateAliasError(alias)
        self.projection_schema[table][alias] = t

    def is_projected(self, expr: Expression) -> bool:
        return self._resolve_projection(expr) is not None

    def _resolve_projection(self, expr: Expression) -> DataType | None:
        name = expr.name
        table = expr.table if isinstance(expr, Column) else None

        if table:
            return self._resolve_qualified_projection(name, table)
        return self._resolve_unqualified_projection(name)

    def _resolve_qualified_projection(self, name: str, table: str) -> DataType | None:
        return self.projection_schema[table].get(name)

    def _resolve_unqualified_projection(self, name: str) -> DataType | None:
        matches = self._find_projection_matches(name)
        return matches[0] if matches else None

    def _find_projection_matches(self, name: str) -> list[DataType]:
        return [schema[name] for schema in self.projection_schema.values() if name in schema]

    # ────── GROUP BY Expression Tracking ──────

    @property
    def is_grouped(self) -> bool:
        return bool(self._group_by_exprs)

    def add_group_by_expr(self, expr: Expression, t: DataType) -> None:
        self._group_by_exprs.append((expr, t))

    def is_group_by_expr(self, expr: Expression) -> bool:
        return self._get_group_by_expr(expr) is not None

    def group_by_expr_t(self, expr: Expression) -> DataType | None:
        expr_t = self._get_group_by_expr(expr)
        assert expr_t is not None  # noqa S101
        _, t = expr_t
        return t

    def _get_group_by_expr(self, expr: Expression) -> tuple[Expression, DataType] | None:
        for grouped, t in self._group_by_exprs:
            if expr == grouped or expr.name == grouped.name:
                return grouped, t
        return None

    # ────── Schema Utilities ──────

    def get_columns(self) -> set[str]:
        return set([col for schema in self._table_schemas.values() for col in schema.keys()])

    def get_schema(self) -> ResultSchema:
        return self._table_schemas

    def get_table_schema(self, table: str) -> ResultSchema:
        if table not in self._table_schemas:
            raise UndefinedTableError(table)
        return {table: self._table_schemas[table]}

    def snapshot_columns(self) -> ColumnTypes:
        column_types = defaultdict(list)
        for _, schema in self._table_schemas.items():
            for col, t in schema.items():
                column_types[col].append(t)
        return column_types

    def validate_star_expansion(self, table: str | None = None) -> ResultSchema:
        schema = self.get_table_schema(table) if table else self.get_schema()

        if self.is_grouped:
            missing: list[str] = []
            for table, table_schema in schema.items():
                for col, _ in table_schema.items():
                    col_expr = Column(this=col, table=table)
                    if not self.is_group_by_expr(col_expr):
                        missing.append(col)

            if missing:
                raise NonGroupedColumnError(missing)

        return schema
