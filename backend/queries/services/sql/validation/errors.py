from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from databases.types import DataType
from sqlglot import Expression


class SQLSemanticError(Exception, ABC):
    @abstractmethod
    def __str__(self) -> str:
        """Provide a human-readable error message."""
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
class NonGroupedColumnError(SQLSemanticError):
    """Raised when one or more non-aggregated columns are not in GROUP BY."""

    columns: Sequence[str]

    def __str__(self) -> str:
        if len(self.columns) == 1:
            return f'column "{self.columns[0]}" must appear in the GROUP BY clause or be used in an aggregate function'
        cols = '", "'.join(self.columns)
        return f'columns "{cols}" must appear in the GROUP BY clause or be used in an aggregate function'


@dataclass
class OrderByPositionError(SQLSemanticError):
    position: int
    max_position: int

    def __str__(self) -> str:
        return f'ORDER BY position {self.position} is not in select list (valid positions: 1 to {self.max_position})'


@dataclass
class OrderByExpressionError(SQLSemanticError):
    expression: Expression

    def __str__(self) -> str:
        return f'ORDER BY expression "{self.expression}" must appear in the SELECT list'


@dataclass
class DuplicateAliasError(SQLSemanticError):
    alias: str

    def __str__(self) -> str:
        return f"Duplicate alias '{self.alias}' in the query."


@dataclass
class MissingJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return 'JOIN requires an ON or USING clause'


@dataclass
class UnorderableTypeError(SQLSemanticError):
    data_type: DataType

    def __str__(self) -> str:
        return f"Cannot order by type '{self.data_type.name}'."


@dataclass
class GroupByClauseRequiredError(SQLSemanticError):
    def __str__(self) -> str:
        return 'HAVING clause requires GROUP BY clause'


@dataclass
class CrossJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return 'CROSS JOIN does not support ON or USING clause'


@dataclass
class NoCommonColumnsError(SQLSemanticError):
    def __str__(self) -> str:
        return 'NATURAL JOIN requires at least one common column'
