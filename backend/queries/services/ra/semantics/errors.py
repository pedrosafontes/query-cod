from dataclasses import dataclass

from ra_sql_visualisation.types import DataType

from ..parser.ast import AggregationFunction, ASTNode, Attribute, SetOperator
from .types import TypedAttribute


@dataclass
class RASemanticError(Exception):
    source: ASTNode

    def __post_init__(self) -> None:
        if self.source.position:
            start_col, end_col = self.source.position
            self.start_col = start_col
            self.end_col = end_col

    def _message(self) -> str:
        raise NotImplementedError('Subclasses must implement _message()')

    def __str__(self) -> str:
        msg = self._message()
        if self.source.position:
            return f'{msg} (Columns {self.start_col}-{self.end_col})'
        return msg


@dataclass
class UndefinedRelationError(RASemanticError):
    relation: str

    def _message(self) -> str:
        return f"Relation '{self.relation}' does not exist"


@dataclass
class UndefinedAttributeError(RASemanticError):
    attribute: Attribute

    def _message(self) -> str:
        return f"Attribute '{self.attribute}' is not defined in the current context"


@dataclass
class AmbiguousAttributeError(RASemanticError):
    attribute: str
    relations: list[set[str]]

    def _message(self) -> str:
        relation_list = ', '.join([f"[{', '.join(rel)}]" for rel in self.relations])
        return f"Attribute '{self.attribute}' is ambiguous - it exists in multiple relations: {relation_list}"


class RATypeError(RASemanticError):
    pass


@dataclass
class InvalidFunctionArgumentError(RATypeError):
    function: AggregationFunction
    expected: list[DataType]
    actual: DataType

    def _message(self) -> str:
        expected_types = ', '.join(str(t) for t in self.expected)
        return f'Invalid argument type for function {self.function.name}: expected one of ({expected_types}), got {self.actual.name}.'


@dataclass
class UnionCompatibilityError(RATypeError):
    operation: SetOperator
    left_attrs: list[TypedAttribute]
    right_attrs: list[TypedAttribute]

    def _message(self) -> str:
        left_attrs = f'({', '.join(attr.name for attr in self.left_attrs)})'
        right_attrs = f'({', '.join(attr.name for attr in self.right_attrs)})'
        return f'Relations in {self.operation.name} are not union-compatible. Left schema: {left_attrs}, Right schema: {right_attrs}'


@dataclass
class TypeMismatchError(RATypeError):
    expected: DataType
    received: DataType
    operation: str = 'operation'

    def _message(self) -> str:
        return f'Type mismatch in {self.operation}: expected {self.expected}, got {self.received}'


@dataclass
class JoinAttributeTypeMismatchError(RATypeError):
    left_attr: TypedAttribute
    right_attr: TypedAttribute

    def _message(self) -> str:
        return f"Type mismatch in join: attribute '{self.left_attr}' has type {self.left_attr.data_type}, but attribute '{self.right_attr}' has type {self.right_attr.data_type}"


@dataclass
class DivisionSchemaMismatchError(RATypeError):
    dividend_attrs: list[TypedAttribute]
    divisor_attrs: list[TypedAttribute]

    def _message(self) -> str:
        dividend_attrs = f'({', '.join(attr.name for attr in self.dividend_attrs)})'
        divisor_attrs = f'({', '.join(attr.name for attr in self.divisor_attrs)})'
        return f'Division schema mismatch: divisor schema is not a subset of dividend schema. Dividend schema: {dividend_attrs}, Divisor schema: {divisor_attrs}'


@dataclass
class DivisionTypeMismatchError(RATypeError):
    dividend_attr: TypedAttribute
    divisor_attr: TypedAttribute

    def _message(self) -> str:
        return f'Attributes of dividend and divisor must match in name and type. Attribute {self.dividend_attr.name} has type {self.dividend_attr.data_type} in dividend and type {self.divisor_attr.data_type} in divisor'
