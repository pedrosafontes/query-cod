from typing import NotRequired, TypedDict

from queries.types import QueryError


class RATree(TypedDict):
    id: int
    label: str
    sub_trees: NotRequired[list['RATree']]
    validation_errors: list[QueryError]
