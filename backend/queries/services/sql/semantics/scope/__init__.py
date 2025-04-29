from __future__ import annotations

from .group_by import GroupByScope
from .projections import ProjectionsScope
from .tables import TablesScope


class Scope:
    def __init__(self, parent: Scope | None = None):
        self.tables: TablesScope = TablesScope(parent.tables if parent else None)
        self.projections = ProjectionsScope()
        self.group_by = GroupByScope()

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by._exprs)
