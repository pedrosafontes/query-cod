from __future__ import annotations

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


@dataclass
class BinaryBooleanExpression:
    left: BooleanExpression
    right: BooleanExpression

    @property
    def operator(self) -> str:
        raise NotImplementedError('Subclasses must implement the operator property')

    def __str__(self) -> str:
        return f'({self.left} {self.operator} {self.right})'


@dataclass
class And(BinaryBooleanExpression):
    @property
    def operator(self) -> str:
        return 'and'


class Or(BinaryBooleanExpression):
    @property
    def operator(self) -> str:
        return 'or'


@dataclass
class Not:
    expression: BooleanExpression

    def __str__(self) -> str:
        return f'(NOT {self.expression})'


ComparisonValue = Attribute | str | int | float | bool


@dataclass
class Comparison(ASTNode):
    left: ComparisonValue
    right: ComparisonValue

    @property
    def operator(self) -> str:
        raise NotImplementedError('Subclasses must implement the operator property')

    def __str__(self) -> str:
        return f'{self.left} {self.operator} {self.right}'


@dataclass
class EQ(Comparison):
    @property
    def operator(self) -> str:
        return '='


@dataclass
class NEQ(Comparison):
    @property
    def operator(self) -> str:
        return '<>'


@dataclass
class GT(Comparison):
    @property
    def operator(self) -> str:
        return '>'


@dataclass
class GTE(Comparison):
    @property
    def operator(self) -> str:
        return '>='


@dataclass
class LT(Comparison):
    @property
    def operator(self) -> str:
        return '<'


@dataclass
class LTE(Comparison):
    @property
    def operator(self) -> str:
        return '<='


BooleanExpression = BinaryBooleanExpression | Not | Comparison | Attribute


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
        if '.' in attr:
            relation, name = attr.split('.', 1)
            return Attribute(name=name, relation=relation)
        else:
            return Attribute(name=attr)
    return attr


class RAQuery(ASTNode):
    def project(
        self, attributes: Sequence[str | Attribute], append: bool = False, optimise: bool = True
    ) -> Projection:
        projections: list[Attribute] = [attribute(attr) for attr in attributes]

        if append and optimise and isinstance(self, Projection):
            projections = projections + self.attributes

        return Projection(
            projections,
            self.subquery if optimise and isinstance(self, Projection) else self,
        )

    def select(self, condition: BooleanExpression) -> Selection:
        return Selection(condition, self)

    def union(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(SetOperator.UNION, self, query(other))

    def intersect(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(SetOperator.INTERSECT, self, query(other))

    def difference(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(SetOperator.DIFFERENCE, self, query(other))

    def cartesian(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(SetOperator.CARTESIAN, self, query(other))

    def natural_join(self, other: RAQuery | str) -> Join:
        return Join(JoinOperator.NATURAL, self, query(other))

    def semi_join(self, other: RAQuery | str) -> Join:
        return Join(JoinOperator.SEMI, self, query(other))

    def anti_join(self, other: RAQuery | str) -> Join:
        return Join(JoinOperator.ANTI, self, query(other))

    def theta_join(self, other: RAQuery | str, condition: BooleanExpression) -> ThetaJoin:
        return ThetaJoin(self, query(other), condition)

    def divide(self, other: RAQuery | str) -> Division:
        return Division(self, query(other))

    def rename(self, alias: str, optimise: bool = True) -> Rename:
        return Rename(alias, self.subquery if optimise and isinstance(self, Rename) else self)

    def grouped_aggregation(
        self, group_by: Sequence[str | Attribute], aggregations: list[Aggregation]
    ) -> GroupedAggregation:
        return GroupedAggregation([attribute(attr) for attr in group_by], aggregations, self)

    def top_n(self, limit: int, attr: str | Attribute) -> TopN:
        return TopN(limit, attribute(attr), self)


def query(relation: RAQuery | str) -> RAQuery:
    if isinstance(relation, str):
        return Relation(name=relation)
    return relation


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
