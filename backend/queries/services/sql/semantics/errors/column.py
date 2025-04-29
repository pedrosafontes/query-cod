from dataclasses import dataclass

from sqlglot.expressions import Column, Expression

from . import SQLSemanticError


@dataclass
class UndefinedColumnError(SQLSemanticError):
    name: str
    table: str | None = None

    @classmethod
    def from_column(cls, column: Column) -> 'UndefinedColumnError':
        return cls(column, column.alias_or_name, column.table)

    @classmethod
    def from_expression(cls, expr: Expression, column: str) -> 'UndefinedColumnError':
        return cls(expr, column)

    def __str__(self) -> str:
        return f"Column '{self.name}' is not defined in {self.table if self.table else 'the current context'}"


@dataclass
class AmbiguousColumnError(SQLSemanticError):
    tables: list[str]

    def __init__(self, column: Column, tables: list[str]) -> None:
        super().__init__(column)
        self.column = column
        self.tables = tables

    def __str__(self) -> str:
        return f"Ambiguous column reference '{self.column}' -  exists in multiple tables: {', '.join(self.tables)}."


@dataclass
class NonGroupedColumnError(SQLSemanticError):
    """Raised when one or more non-aggregated columns are not in GROUP BY."""

    columns: list[str]

    def __str__(self) -> str:
        if len(self.columns) == 1:
            return f'column "{self.columns[0]}" must appear in the GROUP BY clause or be used in an aggregate function'
        cols = '", "'.join(self.columns)
        return f'columns "{cols}" must appear in the GROUP BY clause or be used in an aggregate function'
