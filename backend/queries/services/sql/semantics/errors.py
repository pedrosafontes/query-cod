from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import Column


@dataclass
class SQLSemanticError(Exception, ABC):
    source: Expression

    @abstractmethod
    def __str__(self) -> str:
        """Provide a human-readable error message."""
        pass


@dataclass
class UndefinedTableError(SQLSemanticError):
    name: str | None = None

    def __str__(self) -> str:
        return f"Table '{self.name or self.source.name}' does not exist"


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
    order_by_pos: int
    max_position: int

    def __str__(self) -> str:
        return f'ORDER BY position {self.order_by_pos} is not in select list (valid positions: 1 to {self.max_position})'


@dataclass
class OrderByExpressionError(SQLSemanticError):
    def __str__(self) -> str:
        return f'ORDER BY expression "{self.source}" must appear in the SELECT list'


@dataclass
class DuplicateAliasError(SQLSemanticError):
    def __str__(self) -> str:
        return f"Duplicate alias '{self.source.alias_or_name}' in the query."


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
class CrossJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return 'CROSS JOIN does not support ON or USING clause'


@dataclass
class MissingDerivedTableAliasError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Every derived table must have its own alias'


@dataclass
class ScalarSubqueryError(SQLSemanticError):
    def __str__(self) -> str:
        return 'scalar subquery must return exactly one column'


@dataclass
class DerivedColumnAliasRequiredError(SQLSemanticError):
    def __str__(self) -> str:
        return f'Derived column {self.source} must have an alias'


@dataclass
class AggregateInWhereError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Aggregate functions cannot be used in the WHERE clause'


@dataclass
class NestedAggregateError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Nested aggregate functions are not allowed'


@dataclass
class ColumnCountMismatchError(SQLSemanticError):
    expected: int
    received: int

    def __str__(self) -> str:
        return f'Column count mismatch: expected {self.expected}, got {self.received}'


@dataclass
class ColumnTypeMismatchError(SQLSemanticError):
    left_type: DataType
    right_type: DataType
    index: int

    def __str__(self) -> str:
        return f'Set operands have incompatible column types at position {self.index + 1}: {self.left_type.name} vs {self.right_type.name}.'


@dataclass
class ArithmeticTypeMismatchError(SQLSemanticError):
    left_t: DataType
    right_t: DataType

    def __str__(self) -> str:
        return f'Invalid operand types for {self.source}: {self.left_t} and {self.right_t}'
