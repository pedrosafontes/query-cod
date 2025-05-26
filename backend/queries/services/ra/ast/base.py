from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    pass


class NodePosition(TypedDict):
    line: int
    start_col: int
    end_col: int


@dataclass(kw_only=True)
class ASTNode:
    position: NodePosition | None = field(default=None, compare=False)
