from dataclasses import dataclass

from queries.services.types import ProjectionSchema
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
    relations: list[str]

    def _message(self) -> str:
        return f"Attribute '{self.attribute}' is ambiguous - it exists in multiple relations: {', '.join(self.relations)}"


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
    name: str
    left_t: DataType
    right_t: DataType

    def _message(self) -> str:
        return f"Type mismatch in join: attribute '{self.name}' has type {self.left_t} in left relation, but type {self.right_t} in right relation"


@dataclass
class DivisionSchemaMismatchError(RATypeError):
    dividend_attrs: ProjectionSchema
    divisor_attrs: ProjectionSchema

    def _message(self) -> str:
        dividend_attrs = f'({', '.join(attr for attr in self.dividend_attrs.keys())})'
        divisor_attrs = f'({', '.join(attr for attr in self.divisor_attrs.keys())})'
        return f'Division schema mismatch: divisor schema is not a subset of dividend schema. Dividend schema: {dividend_attrs}, Divisor schema: {divisor_attrs}'


@dataclass
class DivisionTypeMismatchError(RATypeError):
    name: str
    dividend_t: DataType
    divisor_t: DataType

    def _message(self) -> str:
        return f'Attributes of dividend and divisor must match in name and type. Attribute {self.name} has type {self.dividend_t} in dividend and type {self.divisor_t} in divisor'
