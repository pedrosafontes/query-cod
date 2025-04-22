from dataclasses import dataclass

from databases.types import DataType


class SQLSemanticError(Exception):
    pass


@dataclass
class UndefinedTableError(SQLSemanticError):
    table: str

    def __str__(self) -> str:
        return f"Table '{self.table}' does not exist"


@dataclass
class UndefinedColumnError(SQLSemanticError):
    column: str
    table: str | None = None

    def __str__(self) -> str:
        return f"Column '{self.column}' is not defined in {self.table if self.table else 'the current context'}"


@dataclass
class AmbiguousColumnError(SQLSemanticError):
    column: str
    tables: list[str]

    def __str__(self) -> str:
        return f"Ambiguous column reference '{self.column}' -  exists in multiple tables: {', '.join(self.tables)}."


@dataclass
class TypeMismatchError(SQLSemanticError):
    expected: DataType
    received: DataType

    def __str__(self) -> str:
        return f'Type mismatch: expected {self.expected.name}, got {self.received.name}.'
