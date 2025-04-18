from databases.types import DataType

from ..parser.ast import AggregationFunction, RAExpression
from .types import TypedAttribute


class RASemanticError(Exception):
    pass


class UndefinedRelationError(RASemanticError):
    def __init__(self, relation: str):
        self.relation = relation


class UndefinedAttributeError(RASemanticError):
    def __init__(self, attribute: str):
        self.attribute = attribute


class AmbiguousAttributeError(RASemanticError):
    def __init__(self, attribute: str, relations: list[set[str]]):
        self.attribute = attribute
        self.relations = relations


class RATypeError(RASemanticError):
    pass


class InvalidFunctionArgumentError(RATypeError):
    def __init__(
        self,
        function: AggregationFunction,
        expected: list[DataType],
        actual: DataType,
    ):
        self.function = function
        self.expected = expected
        self.actual = actual


class UnionCompatibilityError(RATypeError):
    def __init__(self, left: RAExpression, right: RAExpression):
        self.left = left
        self.right = right


class TypeMismatchError(RATypeError):
    def __init__(self, left: DataType, right: DataType):
        self.left = left
        self.right = right


class JoinAttributeTypeMismatchError(RATypeError):
    def __init__(self, left_attr: TypedAttribute, left_b_attr: TypedAttribute):
        self.left_attr = left_attr
        self.left_b_attr = left_b_attr
