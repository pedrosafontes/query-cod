from abc import ABC
from dataclasses import dataclass

from queries.services.ra.parser.ast import AggregationFunction, SetOperator
from queries.services.types import AttributeSchema
from ra_sql_visualisation.types import DataType

from ..types import TypedAttribute
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
        return f'Invalid argument type for function {self.function.name}'

    @property
    def description(self) -> str:
        expected_types = ', '.join(str(t) for t in self.expected)
        return f'Expected one of ({expected_types}), got {self.actual.name}.'


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
        return f'Left schema: {left_attrs}\n\n' f'Right schema: {right_attrs}'


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
        return f'Expected {self.expected}, got {self.received}'


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


@dataclass
class DivisionSchemaCompatibilityError(RATypeError):
    dividend_attrs: AttributeSchema
    divisor_attrs: AttributeSchema

    @property
    def title(self) -> str:
        return 'Divisor schema is not a subset of dividend schema'

    @property
    def description(self) -> str:
        dividend_attrs = f'({', '.join(attr for attr in self.dividend_attrs.keys())})'
        divisor_attrs = f'({', '.join(attr for attr in self.divisor_attrs.keys())})'
        return f'Dividend schema: {dividend_attrs}<br /><br />Divisor schema: {divisor_attrs}'


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
