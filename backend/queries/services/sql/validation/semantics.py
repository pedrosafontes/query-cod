from typing import cast

from databases.types import DataType, Schema, TableSchema
from sqlglot import Expression
from sqlglot.expressions import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    Add,
    Alias,
    And,
    Avg,
    Column,
    Count,
    Div,
    From,
    Identifier,
    Join,
    Literal,
    Max,
    Min,
    Mul,
    Not,
    Or,
    Select,
    Star,
    Sub,
    Subquery,
    Sum,
    Table,
)

from .errors import (
    CrossJoinConditionError,
    DerivedColumnAliasRequiredError,
    GroupByClauseRequiredError,
    MissingDerivedTableAliasError,
    MissingJoinConditionError,
    NoCommonColumnsError,
    NonGroupedColumnError,
    OrderByExpressionError,
    OrderByPositionError,
    ScalarSubqueryError,
    TypeMismatchError,
    UndefinedColumnError,
    UndefinedTableError,
    UnorderableTypeError,
)
from .scope import ColumnTypes, ResultSchema, Scope
from .utils import infer_literal_type


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, expression: Select) -> None:
        self._validate_select(expression, outer_scope=None)

    def _validate_select(self, select: Select, outer_scope: Scope | None) -> ResultSchema:
        scope = Scope(outer_scope)
        self._populate_from(select, scope)
        self._validate_joins(select, scope)
        self._validate_where(select, scope)
        self._validate_group_by(select, scope)
        self._validate_having(select, scope)
        self._validate_projection(select, scope)
        self._validate_order_by(select, scope)
        return scope.projection_schema

    # ──────── Clause Validators ────────

    def _populate_from(self, select: Select, scope: Scope) -> None:
        from_clause = select.args.get('from')
        if not isinstance(from_clause, From):
            raise NotImplementedError(f'Unsupported FROM clause: {type(from_clause)}')
        self._add_table(from_clause.this, scope)

    def _validate_joins(self, select: Select, scope: Scope) -> None:
        for join in select.args.get('joins', []):
            if not isinstance(join, Join):
                raise NotImplementedError(f'Unsupported join type: {type(join)}')

            left_cols = scope.snapshot_columns()
            self._add_table(join.this, scope)
            right_cols = self.schema[join.this.name]

            kind = join.method or join.args.get('kind', 'INNER')
            using = join.args.get('using')
            condition = join.args.get('on')

            if using:
                self._validate_using(using, left_cols, right_cols)
            elif kind == 'NATURAL':
                self._validate_natural_join(left_cols, right_cols, scope)
            elif kind == 'CROSS':
                if condition:
                    raise CrossJoinConditionError()
            else:  # INNER/LEFT/RIGHT/FULL
                if not condition:
                    raise MissingJoinConditionError()
                condition_t = cast(DataType, self._validate_expression(condition, scope))
                self._assert_boolean(condition_t)

    def _validate_where(self, select: Select, scope: Scope) -> None:
        where = select.args.get('where')
        if where:
            condition_t = cast(DataType, self._validate_expression(where.this, scope))
            self._assert_boolean(condition_t)

    def _validate_group_by(self, select: Select, scope: Scope) -> None:
        group = select.args.get('group')
        if not group:
            return
        for expr in group.expressions:
            self._validate_expression(expr, scope, in_group_by=True)
            scope.group_by.add(expr.name)

    def _validate_having(self, select: Select, scope: Scope) -> None:
        having = select.args.get('having')
        if not having:
            return
        if not scope.group_by:
            raise GroupByClauseRequiredError()
        condition_t = cast(DataType, self._validate_expression(having.this, scope))
        self._assert_boolean(condition_t)

    def _validate_projection(self, select: Select, scope: Scope) -> None:
        for expr in select.expressions:
            t = self._validate_expression(expr, scope)
            if isinstance(t, DataType):
                scope.add_select_item(expr.args.get('table'), expr.alias_or_name, t)
            else:
                for table, columns in t.items():
                    for col, col_type in columns.items():
                        scope.add_select_item(table, col, col_type)

    def _validate_order_by(self, select: Select, scope: Scope) -> None:
        order = select.args.get('order')
        if not order:
            return

        num_projections = len(select.expressions)
        for item in order.expressions:
            node = item.this
            if isinstance(node, Literal):
                if not node.is_int:
                    raise TypeMismatchError(DataType.INTEGER, infer_literal_type(node))
                pos = int(node.this)
                if not (1 <= pos <= num_projections):
                    raise OrderByPositionError(1, num_projections)
                continue

            # in grouped queries must refer to output
            if scope.group_by:
                if node not in select.expressions and not scope.is_projected(node):
                    raise OrderByExpressionError(node)
            else:
                t = cast(DataType, self._validate_expression(node, scope, in_order_by=True))
                if not t.is_orderable():
                    raise UnorderableTypeError(t)

    # ──────── Join Helpers ────────

    def _validate_using(
        self, using: list[Identifier], left_cols: ColumnTypes, right_cols: TableSchema
    ) -> None:
        for ident in using:
            col = ident.name
            col_types = left_cols.get(col, [])
            if not col_types:
                raise UndefinedColumnError(col)
            rhs = right_cols[col]
            for lhs in col_types:
                self._assert_comparable(lhs, rhs)

    def _validate_natural_join(
        self, left_cols: ColumnTypes, right_cols: TableSchema, scope: Scope
    ) -> None:
        shared = set(left_cols.keys()) & set(right_cols)
        if not shared:
            raise NoCommonColumnsError()
        for col in shared:
            rhs = right_cols[col]
            for lhs in left_cols[col]:
                self._assert_comparable(lhs, rhs)

    # ──────── Table & Expression ────────

    def _add_table(self, table: Table | Subquery, scope: Scope) -> None:
        match table:
            case Table():
                name = table.name
                alias = table.alias_or_name
                table_schema = self.schema.get(name)
                if table_schema is None:
                    raise UndefinedTableError(name)
                scope.register_table(alias, table_schema)
            case Subquery():
                alias = table.alias_or_name
                if not alias:
                    raise MissingDerivedTableAliasError()
                sub_select = table.this
                for expr in sub_select.expressions:
                    if not expr.alias_or_name:
                        raise DerivedColumnAliasRequiredError(expr)
                # TODO: Can a subquery's schema have more than one table?
                [(_, sub_schema)] = self._validate_select(sub_select, scope).items()
                scope.register_table(alias, sub_schema)

    def _validate_expression(
        self,
        node: Expression,
        scope: Scope,
        in_group_by: bool = False,
        in_aggregate: bool = False,
        in_order_by: bool = False,
    ) -> DataType | ResultSchema:
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                if isinstance(node.this, Star):
                    return scope.get_table_schema(node.table)
                else:
                    t = scope.resolve_column(node, in_order_by)
                    if (
                        scope.group_by
                        and not in_group_by
                        and not in_aggregate
                        and node.name not in scope.group_by
                    ):
                        raise NonGroupedColumnError([node.name])
                    return t

            case Alias():
                return self._validate_expression(
                    node.this, scope, in_group_by, in_aggregate, in_order_by
                )

            case And() | Or():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_boolean(lt)
                self._assert_boolean(rt)
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Add() | Sub() | Mul() | Div():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_numeric(lt)
                self._assert_numeric(rt)
                return DataType.NUMERIC

            case Not():
                t = cast(
                    DataType,
                    self._validate_expression(
                        node.this, scope, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_boolean(t)
                return DataType.BOOLEAN

            case Count():
                arg = node.this
                if not isinstance(arg, Star):
                    self._validate_expression(
                        arg, scope, in_group_by, in_aggregate=True, in_order_by=in_order_by
                    )
                return DataType.INTEGER

            case Avg() | Sum() | Min() | Max():
                t = cast(
                    DataType,
                    self._validate_expression(
                        node.this, scope, in_group_by, in_aggregate=True, in_order_by=in_order_by
                    ),
                )
                self._assert_numeric(t)
                return DataType.NUMERIC

            case Star():
                if scope.group_by:
                    missing = scope.get_columns() - scope.group_by
                    if missing:
                        raise NonGroupedColumnError(list(missing))
                return scope.get_schema()

            case Subquery():
                sub_schema = self._validate_select(node.this, scope)
                try:
                    self._assert_scalar(node)
                    [(_, columns)] = sub_schema.items()
                    [(_, dtype)] = columns.items()
                except ValueError:
                    raise ScalarSubqueryError() from None
                return dtype

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    # ──────── Type Assertions ────────

    def _assert_comparable(self, lhs: DataType, rhs: DataType) -> None:
        if not lhs.is_comparable_with(rhs):
            raise TypeMismatchError(lhs, rhs)

    def _assert_boolean(self, t: DataType) -> None:
        if t is not DataType.BOOLEAN:
            raise TypeMismatchError(DataType.BOOLEAN, t)

    def _assert_numeric(self, t: DataType) -> None:
        if not t.is_numeric():
            raise TypeMismatchError(DataType.NUMERIC, t)

    def _assert_scalar(self, subquery: Subquery) -> None:
        select = subquery.this
        [scalar] = select.expressions
        group = select.args.get('group')
        if not isinstance(scalar, Count | Sum | Avg | Min | Max) or group:
            raise ScalarSubqueryError()
