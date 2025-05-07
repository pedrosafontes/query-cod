from typing import NotRequired, TypedDict


class RATree(TypedDict):
    label: str
    sub_trees: NotRequired[list['RATree']]
