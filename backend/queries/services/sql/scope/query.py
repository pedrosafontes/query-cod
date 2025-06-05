from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

from queries.services.types import Attributes, RelationalSchema, SQLQuery
from sqlglot.expressions import (
    Column,
    Expression,
    From,
    Identifier,
    Join,
    Select,
    SetOperation,
    Subquery,
    column,
)

from .group_by import GroupByExpressions
from .projections import Projections
from .tables import TablesScope


class SQLScope(ABC):
    def __init__(self, db_schema: RelationalSchema):
        self.db_schema = db_schema

    @property
    @abstractmethod
    def query(self) -> SQLQuery:
        ...

    @property
    @abstractmethod
    def tables(self) -> TablesScope:
        ...

    @property
    @abstractmethod
    def projections(self) -> Projections:
        ...

    def find(self, expr: Expression) -> SQLScope | None:
        if isinstance(expr, SQLQuery):
            query = expr
        else:
            query = cast(Select, expr.parent_select)

        return self._find(query)

    @abstractmethod
    def _find(self, query: SQLQuery) -> SQLScope | None:
        ...


class SelectScope(SQLScope):
    def __init__(self, select: Select, db_schema: RelationalSchema, parent: SQLScope | None):
        super().__init__(db_schema)
        self.select = select
        self._tables: TablesScope = TablesScope(self, parent.tables if parent else None)
        self._projections = Projections()
        self.group_by = GroupByExpressions(select.args.get('group', []))
        self.subquery_scopes: dict[SQLQuery, SQLScope] = {}
        self.joined_left_cols: dict[Join, Attributes] = {}

    @property
    def query(self) -> Select:
        return self.select

    @property
    def tables(self) -> TablesScope:
        return self._tables

    @property
    def projections(self) -> Projections:
        return self._projections

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by.exprs)

    @property
    def from_(self) -> From | None:
        return self.select.args.get('from')

    @property
    def joins(self) -> list[Join]:
        return cast(list[Join], self.select.args.get('joins', []))

    @property
    def where(self) -> Expression | None:
        return self.select.args.get('where')

    @property
    def group(self) -> Expression | None:
        return self.select.args.get('group')

    @property
    def having(self) -> Expression | None:
        return self.select.args.get('having')

    @property
    def order_by(self) -> Expression | None:
        return self.select.args.get('order')

    def expand_star(self, star: Expression) -> list[Column] | None:
        if not star.is_star:
            raise ValueError('Expected a star expression')

        table_ident: Identifier | None = star.args.get('table')

        if table_ident:
            table = table_ident.this
            columns = self.tables.find_columns(table)
            if columns is None:
                return None
            schema = {table: columns}
        else:
            schema = self.tables.get_schema()

        return [column(col, table) for table, cols in schema.items() for col in cols.keys()]

    def _find(self, query: SQLQuery) -> SQLScope | None:
        if query == self.query:
            return self

        scope: SQLScope
        for scope in self.tables.derived_table_scopes.values():
            if query_scope := scope._find(query):
                return query_scope

        for scope in self.subquery_scopes.values():
            if query_scope := scope._find(query):
                return query_scope

        return None


class SetOperationScope(SQLScope):
    def __init__(
        self,
        set_operation: SetOperation,
        db_schema: RelationalSchema,
        left: SQLScope,
        right: SQLScope,
    ):
        super().__init__(db_schema)
        self.set_operation = set_operation
        self.left = left
        self.right = right

    @property
    def query(self) -> SetOperation:
        return self.set_operation

    @property
    def tables(self) -> TablesScope:
        return self.left.tables

    @property
    def projections(self) -> Projections:
        return self.left.projections

    def _find(self, query: SQLQuery) -> SQLScope | None:
        if query == self.query:
            return self
        return self.left._find(query) or self.right._find(query)


class DerivedTableScope(SQLScope):
    def __init__(self, subquery: Subquery, db_schema: RelationalSchema, child: SQLScope):
        super().__init__(db_schema)
        self.subquery = subquery
        self.child = child

    @property
    def query(self) -> Subquery:
        return self.subquery

    @property
    def tables(self) -> TablesScope:
        return self.child.tables

    @property
    def projections(self) -> Projections:
        return self.child.projections

    def _find(self, query: SQLQuery) -> SQLScope | None:
        return self.child._find(query)
