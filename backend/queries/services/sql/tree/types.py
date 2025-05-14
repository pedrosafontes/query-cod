import abc
from dataclasses import dataclass

from queries.types import QueryError


@dataclass
class SQLTree(abc.ABC):
    id: int
    children: list['SQLTree'] | None
    validation_errors: list[QueryError]


@dataclass
class TableNode(SQLTree):
    name: str


@dataclass
class AliasNode(SQLTree):
    alias: str


@dataclass
class JoinNode(SQLTree):
    method: str
    condition: str | None
    using: list[str] | None


@dataclass
class SelectNode(SQLTree):
    columns: list[str]


@dataclass
class WhereNode(SQLTree):
    condition: str


@dataclass
class GroupByNode(SQLTree):
    keys: list[str]


@dataclass
class HavingNode(SQLTree):
    condition: str


@dataclass
class OrderByNode(SQLTree):
    keys: list[str]


@dataclass
class SetOpNode(SQLTree):
    operator: str
