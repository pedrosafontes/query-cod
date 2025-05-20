from typing import cast

from queries.services.types import Attributes, RelationalSchema, SQLQuery, flatten
from sqlglot.expressions import (
    Expression,
    From,
    Identifier,
    Join,
    Select,
    Subquery,
    Table,
)

from ..inference import TypeInferrer
from ..types import SetOperation
from .query import SelectScope, SetOperationScope, SQLScope


def build_scope(
    query: SQLQuery, schema: RelationalSchema, parent: SQLScope | None = None
) -> SQLScope:
    match query:
        case Select():
            return _build_select_scope(query, schema, parent)
        case _ if isinstance(query, SetOperation):
            return _build_set_operation_scope(query, schema, parent)


def _build_set_operation_scope(
    query: SetOperation, schema: RelationalSchema, parent: SQLScope | None = None
) -> SetOperationScope:
    left = build_scope(query.left, schema, parent)
    right = build_scope(query.right, schema, parent)
    scope = SetOperationScope(query, left, right)
    return scope


def _build_select_scope(
    select: Select, schema: RelationalSchema, parent: SQLScope | None = None
) -> SelectScope:
    scope = SelectScope(select, schema, parent)
    _process_from(scope)
    _process_joins(scope)
    _process_where(scope)
    _process_select(scope)
    return scope


def _process_from(scope: SelectScope) -> None:
    from_clause: From | None = scope.query.args.get('from')
    if from_clause:
        _process_table(scope, from_clause.this)


def _process_where(scope: SelectScope) -> None:
    where: Expression | None = scope.query.args.get('where')
    if where:
        for query in where.find_all(Subquery, Select):
            if isinstance(query, Subquery):
                query = query.this
            scope.subquery_scopes[query] = build_scope(query, scope.db_schema, scope)


def _process_joins(scope: SelectScope) -> None:
    joins: list[Join] = scope.query.args.get('joins', [])

    for join in joins:
        left_schema = scope.tables.get_schema()
        scope.join_schemas[join] = left_schema

        table = join.this

        left_cols = flatten(left_schema)
        right_cols = _process_table(scope, table)

        kind = join.method or join.kind
        using: list[Identifier] | None = join.args.get('using')

        if using or kind == 'NATURAL':
            shared_columns = list(set(left_cols) & set(right_cols))
            join_columns = [ident.name for ident in using] if using else shared_columns

            for col in join_columns:
                scope.tables.merge_column(col)


def _process_select(scope: SelectScope) -> None:
    for expr in cast(list[Expression], scope.query.expressions):
        if expr.is_star:
            for col in scope.expand_star(expr) or []:
                scope.projections.add(col, TypeInferrer(scope).infer(col))
        else:
            scope.projections.add(expr, TypeInferrer(scope).infer(expr))


def _process_table(scope: SelectScope, table: Table | Subquery) -> Attributes:
    match table:
        case Table():
            attributes = scope.db_schema.get(table.name, {}).copy()

        case Subquery():
            query = table.this
            child = build_scope(query, scope.db_schema, scope)
            scope.derived_table_scopes[query] = child

            attributes = flatten(child.projections.schema)

    scope.tables.add(table, attributes)

    return attributes
