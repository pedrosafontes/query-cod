from dataclasses import dataclass

from databases.types import DataType
from sqlglot import Expression


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


@dataclass
class GroupByError(SQLSemanticError):
    column: str

    def __str__(self) -> str:
        return (
            f"Column '{self.column}' must appear in the GROUP BY clause "
            f'or be used in an aggregate function.'
        )


@dataclass
class OrderByPositionError(SQLSemanticError):
    position: int
    max_position: int

    def __str__(self) -> str:
        return (
            f'Invalid position {self.position} in ORDER BY - '
            f'must be between 1 and number of select items.'
        )


@dataclass
class OrderByExpressionError(SQLSemanticError):
    expression: Expression

    def __str__(self) -> str:
        return (
            f'Invalid expression {self.expression} in ORDER BY - '
            f'must be a column name or an aggregate function.'
        )
    
@dataclass
class DuplicateAliasError(SQLSemanticError):
    alias: str

    def __str__(self) -> str:
        return f"Duplicate alias '{self.alias}' in the query."

@dataclass
class MissingJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return f"Missing join condition."
    
@dataclass
class UnorderableTypeError(SQLSemanticError):
    data_type: DataType

    def __str__(self) -> str:
        return f"Cannot order by type '{self.data_type.name}' - it is not orderable."