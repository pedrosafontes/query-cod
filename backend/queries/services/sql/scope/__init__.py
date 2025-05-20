from __future__ import annotations

from typing import cast

from queries.services.types import Attributes, RelationalSchema, SQLQuery, flatten
from sqlglot.expressions import (
    Column,
    Expression,
    From,
    Identifier,
    Join,
    Select,
    Star,
    Subquery,
    Table,
)

from ..types import SetOperation
from .group_by import GroupByScope
from .projections import ProjectionsScope
from .tables import TablesScope


class SQLScope:
    @classmethod
    def build(
        cls, query: SQLQuery, schema: RelationalSchema, parent: SQLScope | None = None
    ) -> SQLScope:
        match query:
            case Select():
                return SelectScope.build(query, schema, parent)
            case _ if isinstance(query, SetOperation):
                return SetOperationScope.build(query, schema, parent)

    @property
    def tables(self) -> TablesScope:
        raise NotImplementedError('Subclasses must implement this method')

    @property
    def projections(self) -> ProjectionsScope:
        raise NotImplementedError('Subclasses must implement this method')


class SetOperationScope(SQLScope):
    def __init__(self, query: SetOperation, left: SQLScope, right: SQLScope):
        self.query = query
        self.left = left
        self.right = right

    @classmethod
    def build(
        cls, query: SQLQuery, schema: RelationalSchema, parent: SQLScope | None = None
    ) -> SetOperationScope:
        if not isinstance(query, SetOperation):
            raise ValueError('Expected a SetOperation query')

        left = SQLScope.build(query.left, schema, parent)
        right = SQLScope.build(query.right, schema, parent)
        scope = cls(query, left, right)
        return scope

    @property
    def tables(self) -> TablesScope:
        return self.left.tables

    @property
    def projections(self) -> ProjectionsScope:
        return self.left.projections


class SelectScope(SQLScope):
    def __init__(self, select: Select, schema: RelationalSchema, parent: SQLScope | None):
        self.query = select
        self.schema = schema
        self._tables: TablesScope = TablesScope(parent.tables if parent else None)
        self._projections = ProjectionsScope()
        self.group_by = GroupByScope()
        self.derived_table_scopes: dict[SQLQuery, SQLScope] = {}
        self.subquery_scopes: dict[SQLQuery, SQLScope] = {}

    @property
    def tables(self) -> TablesScope:
        return self._tables

    @property
    def projections(self) -> ProjectionsScope:
        return self._projections

    def get_columns(self, table: Table | Subquery) -> Attributes:
        match table:
            case Table():
                return self._get_base_table_attributes(table)

            case Subquery():
                return self._get_derived_table_attributes(table)

    def get_schema(self, table: Table | Subquery) -> RelationalSchema:
        name = table.alias_or_name
        return {name: self.get_columns(table)}

    @property
    def is_grouped(self) -> bool:
        return bool(self.group_by._exprs)

    @classmethod
    def build(
        cls, select: SQLQuery, schema: RelationalSchema, parent: SQLScope | None = None
    ) -> SelectScope:
        if not isinstance(select, Select):
            raise ValueError('Expected a Select query')

        scope = cls(select, schema, parent)
        scope._process_from(select)
        scope._process_joins(select)
        scope._process_where(select)
        scope._process_group_by(select)
        scope._process_select(select)
        return scope

    def _process_from(self, select: Select) -> None:
        from_clause: From | None = select.args.get('from')
        if from_clause:
            self._process_table(from_clause.this)

    def _process_where(self, select: Select) -> None:
        where: Expression | None = select.args.get('where')
        if where:
            for query in where.find_all(Subquery, Select):
                if isinstance(query, Subquery):
                    query = query.this
                self.subquery_scopes[query] = SQLScope.build(query, self.schema, self)

    def _process_joins(self, select: Select) -> None:
        joins: list[Join] = select.args.get('joins', [])

        for join in joins:
            table = join.this

            left_cols = self._tables.get_columns()
            right_cols = self.get_columns(table)

            self._process_table(table)

            kind = join.method or join.args.get('kind', 'INNER')
            using: list[Identifier] | None = join.args.get('using')

            if using or kind == 'NATURAL':
                shared_columns = list(set(left_cols) & set(right_cols))
                join_columns = [ident.name for ident in using] if using else shared_columns

                for col in join_columns:
                    self._tables.merge_common_column(col)

    def _process_group_by(self, select: Select) -> None:
        group = select.args.get('group')
        if group:
            expressions: list[Expression] = group.expressions
            self.group_by.add(expressions)

    def _process_select(self, select: Select) -> None:
        from ..inference import TypeInferrer

        for expr in cast(list[Expression], select.expressions):
            inner: Expression = expr.unalias()  # type: ignore[no-untyped-call]
            if inner.is_star:
                for col in self.expand_star(expr):
                    self._projections.add(col, TypeInferrer(self).infer(col))
            else:
                self._projections.add(expr, TypeInferrer(self).infer(expr))

    def expand_star(self, star: Column | Star) -> list[Column]:
        table_ident: Identifier | None = star.args.get('table')

        schema = (
            self._tables.get_table_schema(table_ident.this, star)
            if table_ident
            else self._tables.get_schema()
        )

        return [
            Column(name=col, table=table) for table, cols in schema.items() for col in cols.keys()
        ]

    def _process_table(self, table: Table | Subquery) -> None:
        self._tables.add(table, self.get_columns(table))

    def _get_base_table_attributes(self, table: Table) -> Attributes:
        return self.schema.get(table.name, {}).copy()

    def _get_derived_table_attributes(self, subquery: Subquery) -> Attributes:
        query = subquery.this
        if subquery in self.derived_table_scopes:
            child = self.derived_table_scopes[query]
        else:
            child = SQLScope.build(query, self.schema, self)
            self.derived_table_scopes[query] = child
        return flatten(child.projections.schema)
