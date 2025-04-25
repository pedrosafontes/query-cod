from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ValidationContext:
    in_where: bool = False
    in_group_by: bool = False
    in_aggregate: bool = False
    in_order_by: bool = False
    in_having: bool = False

    def enter_aggregate(self) -> ValidationContext:
        return replace(self, in_aggregate=True)
