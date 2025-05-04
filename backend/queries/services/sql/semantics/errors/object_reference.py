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

    @property
    def title(self) -> str:
        return f'Relation `{self.name or self.source.name}` does not exist'

    @property
    def hint(self) -> str:
        return 'Make sure the relation name is correct and visible from the current query scope.'


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

    @property
    def title(self) -> str:
        return f"Column `{self.name}` is not defined in {self.table if self.table else 'the current context'}"

    @property
    def hint(self) -> str:
        return 'Make sure the column name is correct and visible from the current query scope.'


@dataclass
class AmbiguousColumnReferenceError(SQLSemanticError):
    tables: list[str]

    def __init__(self, column: Column, tables: list[str]) -> None:
        super().__init__(column)
        self.column = column
        self.tables = tables

    @property
    def title(self) -> str:
        return f'Ambiguous reference to column `{self.column.name}`'

    @property
    def description(self) -> str:
        return f"It exists in multiple tables: {', '.join(self.tables)}."

    @property
    def hint(self) -> str:
        return 'Qualify the column with its table or alias, e.g. `R.column_name`.'
