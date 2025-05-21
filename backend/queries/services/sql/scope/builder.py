from typing import cast

from queries.services.types import Attributes, RelationalSchema, SQLQuery, flatten
from sqlglot.expressions import (
    Expression,
    Identifier,
    Select,
    SetOperation,
    Subquery,
    Table,
)

from ..inference import TypeInferrer
from ..types import SQLTable
from .query import DerivedTableScope, SelectScope, SetOperationScope, SQLScope


def build_scope(
    query: SQLQuery, schema: RelationalSchema, parent: SQLScope | None = None
) -> SQLScope:
    match query:
        case Select():
            return _build_select_scope(query, schema, parent)
        case _ if isinstance(query, SetOperation):
            return _build_set_operation_scope(query, schema, parent)
        case Subquery():
            return _build_derived_table_scope(query, schema, parent)
        case _:
            raise NotImplementedError(f'Unsupported query type: {type(query)}')


def _build_derived_table_scope(
    subquery: Subquery, schema: RelationalSchema, parent: SQLScope | None = None
) -> DerivedTableScope:
    child = build_scope(subquery.this, schema, parent)
    return DerivedTableScope(subquery, child)


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
    if scope.from_:
        _process_table(scope, scope.from_.this)


def _process_where(scope: SelectScope) -> None:
    if scope.where:
        for query in scope.where.find_all(Subquery, Select):
            if isinstance(query, Subquery):
                query = query.this
            scope.subquery_scopes[query] = build_scope(query, scope.db_schema, scope)


def _process_joins(scope: SelectScope) -> None:
    for join in scope.joins:
        left_cols = scope.tables.get_all_columns()
        scope.joined_left_cols[join] = left_cols

        table = join.this

        right_cols = _process_table(scope, table)

        kind = join.method or join.kind
        using: list[Identifier] | None = join.args.get('using')

        if using or kind == 'NATURAL':
            shared_columns = list(set(left_cols) & set(right_cols))
            join_columns = [ident.name for ident in using] if using else shared_columns

            for col in join_columns:
                scope.tables.merge_column(col)


def _process_select(scope: SelectScope) -> None:
    for expr in cast(list[Expression], scope.select.expressions):
        if expr.is_star:
            for col in scope.expand_star(expr) or []:
                scope.projections.add(col, TypeInferrer(scope).infer(col))
        else:
            scope.projections.add(expr, TypeInferrer(scope).infer(expr))


def _process_table(scope: SelectScope, table: SQLTable) -> Attributes:
    match table:
        case Table():
            attributes = scope.db_schema.get(table.name, {}).copy()

        case Subquery():
            derived_table_scope = _build_derived_table_scope(table, scope.db_schema, scope)
            scope.tables.derived_table_scopes[table.alias_or_name] = derived_table_scope

            attributes = flatten(derived_table_scope.projections.schema)

    scope.tables.add(table, attributes)

    return attributes
