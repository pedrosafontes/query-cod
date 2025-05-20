from __future__ import annotations

from queries.services.types import RelationalSchema, SQLQuery
from sqlglot.expressions import Column, Expression, Identifier, Join, Select, SetOperation

from .group_by import GroupByScope
from .projections import ProjectionsScope
from .tables import TablesScope


class SQLScope:
    @property
    def tables(self) -> TablesScope:
        raise NotImplementedError('Subclasses must implement this method')

    @property
    def projections(self) -> ProjectionsScope:
        raise NotImplementedError('Subclasses must implement this method')


class SelectScope(SQLScope):
    def __init__(self, select: Select, schema: RelationalSchema, parent: SQLScope | None):
        self.query = select
        self.db_schema = schema
        self._tables: TablesScope = TablesScope(parent.tables if parent else None)
        self._projections = ProjectionsScope()
        self.group_by = GroupByScope(select.args.get('group', []))
        self.derived_table_scopes: dict[SQLQuery, SQLScope] = {}
        self.subquery_scopes: dict[SQLQuery, SQLScope] = {}
        self.join_schemas: dict[Join, RelationalSchema] = {}

    @property
    def tables(self) -> TablesScope:
        return self._tables

    @property
    def projections(self) -> ProjectionsScope:
        return self._projections

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by.exprs)

    def expand_star(self, star: Expression) -> list[Column] | None:
        if not star.is_star:
            raise ValueError('Expected a star expression')

        table_ident: Identifier | None = star.args.get('table')

        if table_ident:
            table_schema = self.tables.get_table_schema(table_ident.this)
            if not table_schema:
                return None
            schema = table_schema
        else:
            schema = self.tables.get_schema()

        return [
            Column(name=col, table=table) for table, cols in schema.items() for col in cols.keys()
        ]


class SetOperationScope(SQLScope):
    def __init__(self, query: SetOperation, left: SQLScope, right: SQLScope):
        self.query = query
        self.left = left
        self.right = right

    @property
    def tables(self) -> TablesScope:
        return self.left.tables

    @property
    def projections(self) -> ProjectionsScope:
        return self.left.projections
