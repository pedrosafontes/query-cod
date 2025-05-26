from abc import ABC
from dataclasses import dataclass

from query_cod.types import DataType

from . import SQLSemanticError


@dataclass
class SQLTypeError(SQLSemanticError, ABC):
    @property
    def title(self) -> str:
        return 'Type error'


@dataclass
class TypeMismatchError(SQLTypeError):
    expected: DataType
    received: DataType

    @property
    def description(self) -> str:
        return f'Type mismatch in `{self.source.sql()}`: expected **{self.expected}**, but got **{self.received}**.'


@dataclass
class ColumnTypeMismatchError(SQLTypeError):
    left_type: DataType
    right_type: DataType
    index: int

    @property
    def title(self) -> str:
        return 'Type mismatch in set operation'

    @property
    def description(self) -> str:
        return f'Column type mismatch at position {self.index + 1}: left type **{self.left_type}**, right type **{self.right_type}**.'


@dataclass
class ArithmeticTypeMismatchError(SQLTypeError):
    left_t: DataType
    right_t: DataType

    @property
    def description(self) -> str:
        return f'Invalid operand types for `{self.source.sql()}`: **{self.left_t}** and **{self.right_t}**'


@dataclass
class NonScalarExpressionError(SQLTypeError):
    @property
    def description(self) -> str:
        return f'Expected a scalar expression from `{self.source.sql()}`'


@dataclass
class InvalidCastError(SQLTypeError):
    source_t: DataType
    target_t: DataType

    @property
    def description(self) -> str:
        return f'Cannot cast `{self.source.this}` of type **{self.source_t}** to type **{self.target_t}**'

    @property
    def hint(self) -> str:
        return 'Check if the value is valid for the target type, or use an intermediate cast if needed.'
