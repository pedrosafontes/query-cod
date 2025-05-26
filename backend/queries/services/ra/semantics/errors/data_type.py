from abc import ABC
from dataclasses import dataclass

from queries.services.ra.ast import AggregationFunction, SetOperator
from queries.services.ra.scope.types import TypedAttribute
from queries.services.types import Attributes
from query_cod.types import DataType

from .base import RASemanticError


class RATypeError(RASemanticError, ABC):
    pass


@dataclass
class InvalidFunctionArgumentError(RATypeError):
    function: AggregationFunction
    expected: list[DataType]
    actual: DataType

    @property
    def title(self) -> str:
        return f'Invalid argument type for function *{self.function}*'

    @property
    def description(self) -> str:
        expected_types = ', '.join(str(t) for t in self.expected)
        return f'Expected one of (**{expected_types}**), got **{self.actual}**.'


@dataclass
class UnionCompatibilityError(RATypeError):
    operation: SetOperator
    left_attrs: list[TypedAttribute]
    right_attrs: list[TypedAttribute]

    @property
    def title(self) -> str:
        return f'Relations in {self.operation.name} are not union-compatible'

    @property
    def description(self) -> str:
        left_attrs = f'({', '.join(attr.name for attr in self.left_attrs)})'
        right_attrs = f'({', '.join(attr.name for attr in self.right_attrs)})'
        return f'**Left schema**: {left_attrs}<br>**Right schema**: {right_attrs}'

    @property
    def hint(self) -> str:
        return 'Ensure both relations in the operation have the same number and type of attributes, in the same order.'


@dataclass
class TypeMismatchError(RATypeError):
    expected: DataType
    received: DataType
    operation: str = 'operation'

    @property
    def title(self) -> str:
        return f'Type mismatch in {self.operation}'

    @property
    def description(self) -> str:
        return f'Expected **{self.expected}**, got **{self.received}**'


@dataclass
class JoinAttributeTypeMismatchError(RATypeError):
    name: str
    left_t: DataType
    right_t: DataType

    @property
    def title(self) -> str:
        return 'Type mismatch in join'

    @property
    def description(self) -> str:
        return f"Attribute '{self.name}' has type {self.left_t} in left relation, but type {self.right_t} in right relation"

    @property
    def hint(self) -> str:
        return f'Ensure that attribute `{self.name}` has matching types in both relations before joining. Use explicit casting if needed.'


@dataclass
class DivisionSchemaCompatibilityError(RATypeError):
    dividend_attrs: Attributes
    divisor_attrs: Attributes

    @property
    def title(self) -> str:
        return 'Divisor schema is not a subset of dividend schema'

    @property
    def description(self) -> str:
        dividend_attrs = f'({', '.join(attr for attr in self.dividend_attrs.keys())})'
        divisor_attrs = f'({', '.join(attr for attr in self.divisor_attrs.keys())})'
        return f'**Dividend schema**: {dividend_attrs}<br>**Divisor schema**: {divisor_attrs}'


@dataclass
class DivisionAttributeTypeMismatchError(RATypeError):
    name: str
    dividend_t: DataType
    divisor_t: DataType

    @property
    def title(self) -> str:
        return 'Attribute type mismatch in division'

    @property
    def description(self) -> str:
        return f'Attribute {self.name} has type {self.dividend_t} in dividend and type {self.divisor_t} in divisor'
