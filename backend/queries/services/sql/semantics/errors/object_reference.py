from abc import ABC
from dataclasses import dataclass

from sqlglot.expressions import Column, Expression

from .base import SQLSemanticError


@dataclass
class ObjectReferenceError(SQLSemanticError, ABC):
    pass


@dataclass
class RelationNotFoundError(SQLSemanticError):
    name: str | None = None

    def __str__(self) -> str:
        return f"Table '{self.name or self.source.name}' does not exist"


@dataclass
class ColumnNotFoundError(SQLSemanticError):
    name: str
    table: str | None = None

    @classmethod
    def from_column(cls, column: Column) -> 'ColumnNotFoundError':
        return cls(column, column.alias_or_name, column.table)

    @classmethod
    def from_expression(cls, expr: Expression, column: str) -> 'ColumnNotFoundError':
        return cls(expr, column)

    def __str__(self) -> str:
        return f"Column '{self.name}' is not defined in {self.table if self.table else 'the current context'}"


@dataclass
class AmbiguousColumnReferenceError(SQLSemanticError):
    tables: list[str]

    def __init__(self, column: Column, tables: list[str]) -> None:
        super().__init__(column)
        self.column = column
        self.tables = tables

    def __str__(self) -> str:
        return f"Ambiguous column reference '{self.column}' -  exists in multiple tables: {', '.join(self.tables)}."
