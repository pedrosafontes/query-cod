from abc import ABC
from dataclasses import dataclass

from ra_sql_visualisation.types import DataType

from . import SQLSemanticError


@dataclass
class SQLTypeError(SQLSemanticError, ABC):
    pass


@dataclass
class TypeMismatchError(SQLTypeError):
    expected: DataType
    received: DataType

    def __str__(self) -> str:
        return f'Type mismatch: expected {self.expected.name}, got {self.received.name}.'


@dataclass
class ScalarSubqueryError(SQLTypeError):
    def __str__(self) -> str:
        return 'scalar subquery must return exactly one column'


@dataclass
class ColumnTypeMismatchError(SQLTypeError):
    left_type: DataType
    right_type: DataType
    index: int

    def __str__(self) -> str:
        return f'Set operands have incompatible column types at position {self.index + 1}: {self.left_type.name} vs {self.right_type.name}.'


@dataclass
class ArithmeticTypeMismatchError(SQLTypeError):
    left_t: DataType
    right_t: DataType

    def __str__(self) -> str:
        return f'Invalid operand types for {self.source}: {self.left_t} and {self.right_t}'


@dataclass
class ScalarExpressionExpectedError(SQLTypeError):
    def __str__(self) -> str:
        return f'Scalar expression expected, but got {self.source}'


@dataclass
class InvalidCastError(SQLTypeError):
    source_t: DataType
    target_t: DataType

    def __str__(self) -> str:
        return f"Cannot cast '{self.source}' of type {self.source_t} to type {self.target_t}"
