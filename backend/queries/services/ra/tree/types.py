import abc
from dataclasses import dataclass

from queries.types import QueryError


@dataclass
class RATree(abc.ABC):
    id: int
    children: list['RATree'] | None
    validation_errors: list[QueryError]


@dataclass
class RelationNode(RATree):
    name: str


@dataclass
class ProjectionNode(RATree):
    attributes: list[str]


@dataclass
class SelectionNode(RATree):
    condition: str


@dataclass
class DivisionNode(RATree):
    pass


@dataclass
class SetOperationNode(RATree):
    operator: str


@dataclass
class JoinNode(RATree):
    operator: str


@dataclass
class ThetaJoinNode(RATree):
    condition: str


@dataclass
class GroupedAggregationNode(RATree):
    group_by: list[str]
    aggregations: list[tuple[str, str, str]]  # (input, function, output)


@dataclass
class TopNNode(RATree):
    limit: int
    attribute: str
