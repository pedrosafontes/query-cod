from typing import NotRequired, TypedDict


class RATree(TypedDict):
    id: int
    label: str
    sub_trees: NotRequired[list['RATree']]
