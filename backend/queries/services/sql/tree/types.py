from dataclasses import dataclass

from queries.types import QueryError


@dataclass
class SQLTreeNode:
    id: int
    children: list['SQLTree']
    validation_errors: list[QueryError]


@dataclass
class TableNode(SQLTreeNode):
    name: str


@dataclass
class AliasNode(SQLTreeNode):
    alias: str


@dataclass
class JoinNode(SQLTreeNode):
    method: str
    condition: str | None
    using: list[str] | None


@dataclass
class SelectNode(SQLTreeNode):
    columns: list[str]


@dataclass
class WhereNode(SQLTreeNode):
    condition: str


@dataclass
class GroupByNode(SQLTreeNode):
    keys: list[str]


@dataclass
class HavingNode(SQLTreeNode):
    condition: str


@dataclass
class OrderByNode(SQLTreeNode):
    keys: list[str]


@dataclass
class SetOpNode(SQLTreeNode):
    operator: str


SQLTree = (
    TableNode
    | AliasNode
    | JoinNode
    | SelectNode
    | WhereNode
    | GroupByNode
    | HavingNode
    | OrderByNode
    | SetOpNode
)
