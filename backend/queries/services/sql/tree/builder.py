from queries.services.types import RelationalSchema, SQLQuery
from queries.types import QueryError
from sqlglot.expressions import From, Join, Select, Subquery, Table, select

from ..semantics import validate_sql_semantics
from ..semantics.types import SetOperation
from .types import (
    AliasNode,
    GroupByNode,
    HavingNode,
    JoinNode,
    OrderByNode,
    SelectNode,
    SetOpNode,
    SQLTree,
    TableNode,
    WhereNode,
)


class SQLTreeBuilder:
    _counter: int
    _subqueries: dict[int, SQLQuery]

    def __init__(self, schema: RelationalSchema):
        self._schema = schema

    def build(self, query: SQLQuery) -> tuple[SQLTree | None, dict[int, SQLQuery]]:
        self._counter = 0
        self._subqueries = {}
        return self._build(query), self._subqueries

    def _add_subquery(self, subquery: SQLQuery) -> tuple[int, list[QueryError]]:
        subquery_id = self._counter
        errors = validate_sql_semantics(subquery, self._schema)
        self._counter += 1
        self._subqueries[subquery_id] = subquery
        return subquery_id, errors

    def _build(self, query: SQLQuery) -> SQLTree | None:
        match query:
            case Select():
                return self._build_select(query)
            case query if isinstance(query, SetOperation):
                return self._build_set_operation(query)
            case Subquery():
                return self._build_subquery(query)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')

    def _build_set_operation(self, query: SetOperation) -> SQLTree:
        left = self._build(query.left)
        right = self._build(query.right)
        query_id, errors = self._add_subquery(query)
        return SetOpNode(
            id=query_id,
            validation_errors=errors,
            operator=type(query).__name__.lower(),
            children=[q for q in [left, right] if q is not None],
        )

    def _build_subquery(self, subquery: Subquery) -> SQLTree:
        subquery_tree = self._build(subquery.this)
        query_id, errors = self._add_subquery(subquery)
        return AliasNode(
            id=query_id,
            validation_errors=errors,
            alias=subquery.alias_or_name,
            children=[subquery_tree] if subquery_tree else [],
        )

    def _build_select(self, query: Select) -> SQLTree | None:
        from_node, from_subquery = self._build_from(query, select('*'))
        if from_node is None:
            return None
        join_node, join_subquery = self._build_joins(query, from_node, from_subquery)
        where_node, where_subquery = self._build_where(query, join_node, join_subquery)
        group_by_node, group_by_subquery = self._build_group_by(query, where_node, where_subquery)
        having_node, having_subquery = self._build_having(query, group_by_node, group_by_subquery)
        projections_node, projections_subquery = self._build_projection(
            query, having_node, having_subquery
        )
        order_by_node, _ = self._build_order_by(query, projections_node, projections_subquery)
        return order_by_node

    def _build_from(self, query: Select, partial_query: Select) -> tuple[SQLTree | None, Select]:
        from_ = query.args.get('from')
        if from_:
            if not isinstance(from_, From):
                raise NotImplementedError(f'Unsupported FROM clause: {type(from_)}')
            return self._build_table(from_.this, partial_query)
        else:
            return None, partial_query

    def _build_table(
        self, table: Table | Subquery, partial_query: Select | None = None
    ) -> tuple[SQLTree, Select]:
        if partial_query is None:
            partial_query = select('*')

        match table:
            case Table():
                return self._build_base_table(table, partial_query)

            case Subquery():
                return self._build_derived_table(table, partial_query)

    def _build_base_table(self, table: Table, partial_query: Select) -> tuple[SQLTree, Select]:
        partial_query = partial_query.from_(table)
        query_id, errors = self._add_subquery(partial_query)
        return TableNode(
            id=query_id,
            validation_errors=errors,
            name=table.name,
            children=[],
        ), partial_query

    def _build_derived_table(
        self, table: Subquery, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        partial_query = partial_query.from_(table)
        subquery_tree = self._build(table.this)
        query_id, errors = self._add_subquery(partial_query)
        return AliasNode(
            id=query_id,
            validation_errors=errors,
            alias=table.alias_or_name,
            children=[subquery_tree] if subquery_tree else [],
        ), partial_query

    def _build_joins(
        self, query: Select, from_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        left = from_node
        for join in query.args.get('joins', []):
            if not isinstance(join, Join):
                raise NotImplementedError(f'Unsupported JOIN clause: {type(join)}')

            partial_query = partial_query.join(join)
            right, _ = self._build_table(join.this)
            condition = join.args.get('on')
            using = join.args.get('using')

            query_id, errors = self._add_subquery(partial_query)
            left = JoinNode(
                id=query_id,
                validation_errors=errors,
                children=[left, right] if right else [left],
                method=join.method or join.args.get('kind', 'INNER'),
                using=[col.name for col in using] if using else None,
                condition=condition.sql() if condition else None,
            )

        return left, partial_query

    def _build_where(
        self, query: Select, join_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        where = query.args.get('where')
        if where:
            partial_query = partial_query.where(where.this)

            query_id, errors = self._add_subquery(partial_query)
            return WhereNode(
                id=query_id,
                validation_errors=errors,
                condition=where.this.sql(),
                children=[join_node],
            ), partial_query
        else:
            return join_node, partial_query

    def _build_group_by(
        self, query: Select, where_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        group_by = query.args.get('group')
        if group_by:
            partial_query = partial_query.group_by(*group_by.expressions).select(
                *group_by.expressions, append=False
            )

            query_id, errors = self._add_subquery(partial_query)
            return GroupByNode(
                id=query_id,
                validation_errors=errors,
                keys=[expr.sql() for expr in group_by.expressions],
                children=[where_node],
            ), partial_query
        else:
            return where_node, partial_query

    def _build_having(
        self, query: Select, group_by_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        having = query.args.get('having')
        if having:
            condition = having.this
            partial_query = partial_query.having(condition)

            query_id, errors = self._add_subquery(partial_query)
            return HavingNode(
                id=query_id,
                validation_errors=errors,
                condition=condition.sql(),
                children=[group_by_node],
            ), partial_query
        else:
            return group_by_node, partial_query

    def _build_projection(
        self, query: Select, having_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        projections = query.expressions
        if projections:
            partial_query = partial_query.select(*projections, append=False)
            query_id, errors = self._add_subquery(partial_query)
            return SelectNode(
                id=query_id,
                validation_errors=errors,
                columns=[expr.sql() for expr in projections],
                children=[having_node],
            ), partial_query
        else:
            return having_node, partial_query

    def _build_order_by(
        self, query: Select, projections_node: SQLTree, partial_query: Select
    ) -> tuple[SQLTree, Select]:
        order_by = query.args.get('order')
        if order_by:
            partial_query = partial_query.order_by(*order_by.expressions)
            query_id, errors = self._add_subquery(partial_query)
            return OrderByNode(
                id=query_id,
                validation_errors=errors,
                keys=[expr.sql() for expr in order_by.expressions],
                children=[projections_node],
            ), partial_query
        else:
            return projections_node, partial_query
