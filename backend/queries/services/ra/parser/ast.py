from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict


class NodePosition(TypedDict):
    line: int
    start_col: int
    end_col: int


@dataclass(kw_only=True)
class ASTNode:
    position: NodePosition | None = field(default=None, compare=False)


class RAQuery(ASTNode):
    pass


@dataclass
class Relation(RAQuery):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass
class Attribute(ASTNode):
    name: str
    relation: str | None = None

    def __str__(self) -> str:
        if self.relation:
            return f'{self.relation}.{self.name}'
        return self.name


class SetOperator(Enum):
    UNION = 'UNION'
    INTERSECT = 'INTERSECT'
    DIFFERENCE = 'DIFFERENCE'
    CARTESIAN = 'CARTESIAN'


class BinaryBooleanOperator(Enum):
    AND = 'AND'
    OR = 'OR'


@dataclass
class BinaryBooleanExpression:
    operator: BinaryBooleanOperator
    left: 'BooleanExpression'
    right: 'BooleanExpression'


@dataclass
class NotExpression:
    expression: 'BooleanExpression'


class ComparisonOperator(Enum):
    EQUAL = '='
    NOT_EQUAL = '<>'
    GREATER_THAN = '>'
    GREATER_THAN_EQUAL = '>='
    LESS_THAN = '<'
    LESS_THAN_EQUAL = '<='

    def __str__(self) -> str:
        return self.value


ComparisonValue = Attribute | str | int | float | bool


@dataclass
class Comparison(ASTNode):
    operator: ComparisonOperator
    left: ComparisonValue
    right: ComparisonValue


BooleanExpression = BinaryBooleanExpression | NotExpression | Comparison | Attribute


@dataclass
class SetOperation(RAQuery):
    operator: SetOperator
    left: RAQuery
    right: RAQuery


class JoinOperator(Enum):
    NATURAL = 'NATURAL'
    SEMI = 'SEMI'


@dataclass
class Join(RAQuery):
    operator: JoinOperator
    left: RAQuery
    right: RAQuery


@dataclass
class Division(RAQuery):
    dividend: RAQuery
    divisor: RAQuery


@dataclass
class ThetaJoin(RAQuery):
    left: RAQuery
    right: RAQuery
    condition: BooleanExpression


@dataclass
class Projection(RAQuery):
    attributes: list[Attribute]
    sub_query: RAQuery


@dataclass
class Selection(RAQuery):
    condition: BooleanExpression
    sub_query: RAQuery


class AggregationFunction(Enum):
    COUNT = 'count'
    SUM = 'sum'
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'

    def __str__(self) -> str:
        return self.value


@dataclass
class Aggregation:
    input: Attribute
    aggregation_function: AggregationFunction
    output: str


@dataclass
class GroupedAggregation(RAQuery):
    group_by: list[Attribute]
    aggregations: list[Aggregation]
    sub_query: RAQuery


@dataclass
class TopN(RAQuery):
    limit: int
    attribute: Attribute
    sub_query: RAQuery
