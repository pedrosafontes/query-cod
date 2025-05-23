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

    def __str__(self) -> str:
        return self.value


class BinaryBooleanOperator(Enum):
    AND = 'AND'
    OR = 'OR'

    def __str__(self) -> str:
        return self.value


@dataclass
class BinaryBooleanExpression:
    operator: BinaryBooleanOperator
    left: 'BooleanExpression'
    right: 'BooleanExpression'

    def __str__(self) -> str:
        return f'({self.left} {self.operator} {self.right})'


@dataclass
class NotExpression:
    expression: 'BooleanExpression'

    def __str__(self) -> str:
        return f'(NOT {self.expression})'


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

    def __str__(self) -> str:
        return f'{self.left} {self.operator} {self.right}'


BooleanExpression = BinaryBooleanExpression | NotExpression | Comparison | Attribute


@dataclass
class SetOperation(RAQuery):
    operator: SetOperator
    left: RAQuery
    right: RAQuery

    def __str__(self) -> str:
        return f'({self.left} {self.operator} {self.right})'


class JoinOperator(Enum):
    NATURAL = 'NATURAL'
    SEMI = 'SEMI'

    def __str__(self) -> str:
        return f'{self.value} JOIN'


@dataclass
class Join(RAQuery):
    operator: JoinOperator
    left: RAQuery
    right: RAQuery

    def __str__(self) -> str:
        return f'({self.left} {self.operator} {self.right})'


@dataclass
class Division(RAQuery):
    dividend: RAQuery
    divisor: RAQuery

    def __str__(self) -> str:
        return f'({self.dividend} / {self.divisor})'


@dataclass
class ThetaJoin(RAQuery):
    left: RAQuery
    right: RAQuery
    condition: BooleanExpression

    def __str__(self) -> str:
        return f'({self.left} JOIN {self.right} ON {self.condition})'


@dataclass
class Projection(RAQuery):
    attributes: list[Attribute]
    subquery: RAQuery

    def __str__(self) -> str:
        return f'PROJECT ({", ".join(str(attr) for attr in self.attributes)}) (\n{self.subquery}\n)'


@dataclass
class Selection(RAQuery):
    condition: BooleanExpression
    subquery: RAQuery

    def __str__(self) -> str:
        return f'SELECT ({self.condition}) (\n{self.subquery}\n)'


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

    def __str__(self) -> str:
        return f'({self.input}, {self.aggregation_function}, {self.output})'


@dataclass
class GroupedAggregation(RAQuery):
    group_by: list[Attribute]
    aggregations: list[Aggregation]
    subquery: RAQuery

    def __str__(self) -> str:
        group_by = ', '.join(str(attr) for attr in self.group_by)
        aggregations = ', '.join(str(agg) for agg in self.aggregations)
        return f'GROUP (({group_by}), ({aggregations})) (\n{self.subquery}\n)'


@dataclass
class TopN(RAQuery):
    limit: int
    attribute: Attribute
    subquery: RAQuery

    def __str__(self) -> str:
        return f'T ({self.limit}, {self.attribute}) (\n{self.subquery}\n)'


@dataclass
class Rename(RAQuery):
    alias: str
    subquery: RAQuery

    def __str__(self) -> str:
        return f'RENAME ({self.alias}) {self.subquery}'
