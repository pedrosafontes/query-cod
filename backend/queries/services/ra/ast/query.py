from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .attribute import Attribute
from .base import ASTNode
from .boolean import BooleanExpression
from .factory import attribute, query


class RAQuery(ASTNode):
    def project(
        self, *attributes: str | Attribute, append: bool = False, optimise: bool = True
    ) -> Projection:
        projections: list[Attribute] = [attribute(attr) for attr in attributes]

        if append and optimise and isinstance(self, Projection):
            projections = projections + self.attributes

        return Projection(
            self.subquery if optimise and isinstance(self, Projection) else self,
            projections,
        )

    def select(self, condition: BooleanExpression) -> Selection:
        return Selection(self, condition)

    def union(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(self, query(other), SetOperator.UNION)

    def intersect(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(self, query(other), SetOperator.INTERSECT)

    def difference(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(self, query(other), SetOperator.DIFFERENCE)

    def cartesian(self, other: RAQuery | str) -> SetOperation:
        return SetOperation(self, query(other), SetOperator.CARTESIAN)

    def natural_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.NATURAL)

    def semi_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.SEMI)

    def anti_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.ANTI)

    def left_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.LEFT)

    def right_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.RIGHT)

    def outer_join(self, other: RAQuery | str) -> Join:
        return Join(self, query(other), JoinOperator.OUTER)

    def theta_join(self, other: RAQuery | str, condition: BooleanExpression) -> ThetaJoin:
        return ThetaJoin(self, query(other), condition)

    def divide(self, other: RAQuery | str) -> Division:
        return Division(self, query(other))

    def rename(self, alias: str, optimise: bool = True) -> Rename:
        return Rename(self.subquery if optimise and isinstance(self, Rename) else self, alias)

    def grouped_aggregation(
        self, group_by: Sequence[str | Attribute], aggregations: list[Aggregation]
    ) -> GroupedAggregation:
        return GroupedAggregation(self, [attribute(attr) for attr in group_by], aggregations)

    def top_n(self, limit: int, attr: str | Attribute) -> TopN:
        return TopN(self, limit, attribute(attr))

    def latex(self, pretty: bool = False) -> str:
        from ..latex.converter import convert

        return convert(self, pretty)


@dataclass(frozen=True)
class Relation(RAQuery):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class UnaryOperation(RAQuery):
    subquery: RAQuery


@dataclass(frozen=True)
class BinaryOperation(RAQuery):
    left: RAQuery
    right: RAQuery


class SetOperator(Enum):
    UNION = 'UNION'
    INTERSECT = 'INTERSECT'
    DIFFERENCE = 'DIFFERENCE'
    CARTESIAN = 'CARTESIAN'

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SetOperation(BinaryOperation):
    operator: SetOperator

    def __str__(self) -> str:
        return f'({self.left}\n{self.operator}\n{self.right})'


class JoinOperator(Enum):
    NATURAL = 'NATURAL'
    SEMI = 'SEMI'
    ANTI = 'ANTI'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    OUTER = 'FULL OUTER'

    def __str__(self) -> str:
        return f'{self.value} JOIN'


@dataclass(frozen=True)
class Join(BinaryOperation):
    operator: JoinOperator

    def __str__(self) -> str:
        return f'({self.left}\n{self.operator}\n{self.right})'


@dataclass(frozen=True)
class Division(BinaryOperation):
    @property
    def dividend(self) -> RAQuery:
        return self.left

    @property
    def divisor(self) -> RAQuery:
        return self.right

    def __str__(self) -> str:
        return f'({self.dividend} / {self.divisor})'


@dataclass(frozen=True)
class ThetaJoin(BinaryOperation):
    condition: BooleanExpression

    def __str__(self) -> str:
        return f'({self.left} JOIN {self.right} ON {self.condition})'


@dataclass(frozen=True)
class Projection(UnaryOperation):
    attributes: list[Attribute]

    def __str__(self) -> str:
        return f'PROJECT ({", ".join(str(attr) for attr in self.attributes)}) (\n{indent(str(self.subquery))}\n)'


@dataclass(frozen=True)
class Selection(UnaryOperation):
    condition: BooleanExpression

    def __str__(self) -> str:
        return f'SELECT ({self.condition}) (\n{indent(str(self.subquery))}\n)'


class AggregationFunction(Enum):
    COUNT = 'count'
    SUM = 'sum'
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Aggregation:
    input: Attribute
    aggregation_function: AggregationFunction
    output: str

    def __str__(self) -> str:
        return f'({self.input}, {self.aggregation_function}, {self.output})'


@dataclass(frozen=True)
class GroupedAggregation(UnaryOperation):
    group_by: list[Attribute]
    aggregations: list[Aggregation]

    def __str__(self) -> str:
        group_by = ', '.join(str(attr) for attr in self.group_by)
        aggregations = ', '.join(str(agg) for agg in self.aggregations)
        return f'GROUP (({group_by}), ({aggregations})) (\n{indent(str(self.subquery))}\n)'


@dataclass(frozen=True)
class TopN(UnaryOperation):
    limit: int
    attribute: Attribute

    def __str__(self) -> str:
        return f'T ({self.limit}, {self.attribute}) (\n{indent(str(self.subquery))}\n)'


@dataclass(frozen=True)
class Rename(UnaryOperation):
    alias: str

    def __str__(self) -> str:
        return f'RENAME ({self.alias}) {self.subquery}'


def indent(text: str) -> str:
    return '\n'.join('    ' + line for line in text.split('\n'))
