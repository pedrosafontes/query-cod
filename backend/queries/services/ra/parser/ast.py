from collections.abc import Callable, Sequence
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


@dataclass
class Attribute(ASTNode):
    name: str
    relation: str | None = None

    def __str__(self) -> str:
        if self.relation:
            return f'{self.relation}.{self.name}'
        return self.name


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


def attribute(attr: str | Attribute) -> Attribute:
    if isinstance(attr, str):
        return Attribute(name=attr)
    return attr


class RAQuery(ASTNode):
    def project(
        self, attributes: Sequence[str | Attribute], append: bool = False, optimise: bool = True
    ) -> 'Projection':
        projections: list[Attribute] = [attribute(attr) for attr in attributes]

        if append and optimise and isinstance(self, Projection):
            projections = projections + self.attributes

        return Projection(
            projections,
            self.subquery if optimise and isinstance(self, Projection) else self,
        )

    def select(self, condition: BooleanExpression) -> 'Selection':
        return Selection(condition, self)

    def union(self, other: 'RAQuery') -> 'SetOperation':
        return SetOperation(SetOperator.UNION, self, other)

    def intersect(self, other: 'RAQuery') -> 'SetOperation':
        return SetOperation(SetOperator.INTERSECT, self, other)

    def difference(self, other: 'RAQuery') -> 'SetOperation':
        return SetOperation(SetOperator.DIFFERENCE, self, other)

    def cartesian(self, other: 'RAQuery') -> 'SetOperation':
        return SetOperation(SetOperator.CARTESIAN, self, other)

    def natural_join(self, other: 'RAQuery') -> 'Join':
        return Join(JoinOperator.NATURAL, self, other)

    def semi_join(self, other: 'RAQuery') -> 'Join':
        return Join(JoinOperator.SEMI, self, other)

    def anti_join(self, other: 'RAQuery') -> 'Join':
        return Join(JoinOperator.ANTI, self, other)

    def theta_join(self, other: 'RAQuery', condition: BooleanExpression) -> 'ThetaJoin':
        return ThetaJoin(self, other, condition)

    def divide(self, other: 'RAQuery') -> 'Division':
        return Division(self, other)

    def rename(self, alias: str) -> 'Rename':
        return Rename(alias, self)

    def grouped_aggregation(
        self, group_by: Sequence[str | Attribute], aggregations: list[Aggregation]
    ) -> 'GroupedAggregation':
        return GroupedAggregation([attribute(attr) for attr in group_by], aggregations, self)

    def top_n(self, limit: int, attr: str | Attribute) -> 'TopN':
        return TopN(limit, attribute(attr), self)


def cartesian(relations: list[RAQuery]) -> RAQuery:
    return _combine_relations(relations, lambda left, right: left.cartesian(right))


def natural_join(relations: list[RAQuery]) -> RAQuery:
    return _combine_relations(relations, lambda left, right: left.natural_join(right))


def anti_join(relations: list[RAQuery]) -> RAQuery:
    return _combine_relations(relations, lambda left, right: left.anti_join(right))


def _combine_relations(
    relations: list[RAQuery], operator: Callable[[RAQuery, RAQuery], RAQuery]
) -> RAQuery:
    if not relations:
        raise ValueError('No relations provided for combination')
    if len(relations) == 1:
        return relations[0]
    result = relations[0]
    for relation in relations[1:]:
        result = operator(result, relation)
    return result


def unnest_cartesian_operands(query: RAQuery) -> list[RAQuery]:
    match query:
        case SetOperation(operator=SetOperator.CARTESIAN):
            return unnest_cartesian_operands(query.left) + unnest_cartesian_operands(query.right)
        case _:
            return [query]


@dataclass
class Relation(RAQuery):
    name: str

    def __str__(self) -> str:
        return self.name


class SetOperator(Enum):
    UNION = 'UNION'
    INTERSECT = 'INTERSECT'
    DIFFERENCE = 'DIFFERENCE'
    CARTESIAN = 'CARTESIAN'

    def __str__(self) -> str:
        return self.value


@dataclass
class SetOperation(RAQuery):
    operator: SetOperator
    left: RAQuery
    right: RAQuery

    def __str__(self) -> str:
        return f'({self.left}\n{self.operator}\n{self.right})'


class JoinOperator(Enum):
    NATURAL = 'NATURAL'
    SEMI = 'SEMI'
    ANTI = 'ANTI'

    def __str__(self) -> str:
        return f'{self.value} JOIN'


@dataclass
class Join(RAQuery):
    operator: JoinOperator
    left: RAQuery
    right: RAQuery

    def __str__(self) -> str:
        return f'({self.left}\n{self.operator}\n{self.right})'


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
        return f'PROJECT ({", ".join(str(attr) for attr in self.attributes)}) (\n{indent(str(self.subquery))}\n)'


@dataclass
class Selection(RAQuery):
    condition: BooleanExpression
    subquery: RAQuery

    def __str__(self) -> str:
        return f'SELECT ({self.condition}) (\n{indent(str(self.subquery))}\n)'


@dataclass
class GroupedAggregation(RAQuery):
    group_by: list[Attribute]
    aggregations: list[Aggregation]
    subquery: RAQuery

    def __str__(self) -> str:
        group_by = ', '.join(str(attr) for attr in self.group_by)
        aggregations = ', '.join(str(agg) for agg in self.aggregations)
        return f'GROUP (({group_by}), ({aggregations})) (\n{indent(str(self.subquery))}\n)'


@dataclass
class TopN(RAQuery):
    limit: int
    attribute: Attribute
    subquery: RAQuery

    def __str__(self) -> str:
        return f'T ({self.limit}, {self.attribute}) (\n{indent(str(self.subquery))}\n)'


@dataclass
class Rename(RAQuery):
    alias: str
    subquery: RAQuery

    def __str__(self) -> str:
        return f'RENAME ({self.alias}) {self.subquery}'


def indent(text: str) -> str:
    return '\n'.join('    ' + line for line in text.split('\n'))
