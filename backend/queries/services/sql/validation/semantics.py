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
    In,
    Join,
    Literal,
    Max,
    Min,
    Mul,
    Not,
    Or,
    Paren,
    Select,
    Star,
    Sub,
    Subquery,
    Sum,
    Table,
)

from .errors import (
    AggregateInWhereError,
    CrossJoinConditionError,
    DerivedColumnAliasRequiredError,
    GroupByClauseRequiredError,
    MissingDerivedTableAliasError,
    MissingJoinConditionError,
    NestedAggregateError,
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
            else:
                if not condition:
                    raise MissingJoinConditionError()
                self._assert_boolean(cast(DataType, self._validate_expression(condition, scope)))

    def _validate_where(self, select: Select, scope: Scope) -> None:
        where = select.args.get('where')
        if where:
            self._assert_boolean(
                cast(DataType, self._validate_expression(where.this, scope, in_where=True))
            )

    def _validate_group_by(self, select: Select, scope: Scope) -> None:
        group = select.args.get('group')
        if group:
            for expr in group.expressions:
                scope.add_group_by_expr(
                    expr, cast(DataType, self._validate_expression(expr, scope, in_group_by=True))
                )

    def _validate_having(self, select: Select, scope: Scope) -> None:
        having = select.args.get('having')
        if having:
            if not scope.is_grouped:
                raise GroupByClauseRequiredError()
            self._assert_boolean(cast(DataType, self._validate_expression(having.this, scope)))

    def _validate_projection(self, select: Select, scope: Scope) -> None:
        for expr in select.expressions:
            t = (
                scope.group_by_expr_t(expr)
                if scope.is_group_by_expr(expr)
                else self._validate_expression(expr, scope)
            )
            if isinstance(t, DataType):
                scope.add_projection(expr.args.get('table'), expr.alias_or_name, t)
            else:
                for table, columns in cast(ResultSchema, t).items():
                    for col, col_type in columns.items():
                        scope.add_projection(table, col, col_type)

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

            if scope.is_grouped:
                if node not in select.expressions and not scope.is_projected(node):
                    raise OrderByExpressionError(node)
            else:
                t = cast(DataType, self._validate_expression(node, scope, in_order_by=True))
                if not t.is_orderable():
                    raise UnorderableTypeError(t)

    # ──────── Join Helpers ────────

    def _validate_using(
        self, using: list[Identifier], left: ColumnTypes, right: TableSchema
    ) -> None:
        for ident in using:
            col = ident.name
            if col not in left:
                raise UndefinedColumnError(col)
            for ltype in left[col]:
                self._assert_comparable(ltype, right[col])

    def _validate_natural_join(self, left: ColumnTypes, right: TableSchema, scope: Scope) -> None:
        shared = set(left) & set(right)
        if not shared:
            raise NoCommonColumnsError()
        for col in shared:
            for ltype in left[col]:
                self._assert_comparable(ltype, right[col])

    # ──────── Table & Expression Validation ────────

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
                [(_, sub_schema)] = self._validate_select(sub_select, scope).items()
                scope.register_table(alias, sub_schema)

    def _validate_expression(
        self,
        node: Expression,
        scope: Scope,
        in_where: bool = False,
        in_group_by: bool = False,
        in_aggregate: bool = False,
        in_order_by: bool = False,
    ) -> DataType | ResultSchema:
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                if isinstance(node.this, Star):
                    return scope.validate_star_expansion(node.table)
                else:
                    t = scope.resolve_column(node, in_order_by)
                    if (
                        scope.is_grouped
                        and not in_group_by
                        and not in_aggregate
                        and not scope.is_group_by_expr(node)
                    ):
                        raise NonGroupedColumnError([node.name])
                    return t

            case Alias():
                return self._validate_expression(
                    node.this, scope, in_where, in_group_by, in_aggregate, in_order_by
                )

            case And() | Or():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_boolean(lt)
                self._assert_boolean(rt)
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Add() | Sub() | Mul() | Div():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.left, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                rt = cast(
                    DataType,
                    self._validate_expression(
                        node.right, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_numeric(lt)
                self._assert_numeric(rt)
                return DataType.NUMERIC

            case Not():
                t = cast(
                    DataType,
                    self._validate_expression(
                        node.this, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                self._assert_boolean(t)
                return DataType.BOOLEAN

            case Count():
                self._validate_aggregate(in_where, in_aggregate)
                arg = node.this
                if not isinstance(arg, Star):
                    self._validate_expression(
                        arg,
                        scope,
                        in_where,
                        in_group_by,
                        in_aggregate=True,
                        in_order_by=in_order_by,
                    )
                return DataType.INTEGER

            case Avg() | Sum() | Min() | Max():
                self._validate_aggregate(in_where, in_aggregate)
                t = cast(
                    DataType,
                    self._validate_expression(
                        node.this,
                        scope,
                        in_where,
                        in_group_by,
                        in_aggregate=True,
                        in_order_by=in_order_by,
                    ),
                )
                self._assert_numeric(t)
                return DataType.NUMERIC

            case Star():
                return scope.validate_star_expansion()

            case Subquery():
                sub_schema = self._validate_select(node.this, scope)
                try:
                    self._assert_scalar(node)
                    [(_, columns)] = sub_schema.items()
                    [(_, t)] = columns.items()
                except ValueError:
                    raise ScalarSubqueryError() from None
                return t

            case In():
                lt = cast(
                    DataType,
                    self._validate_expression(
                        node.this, scope, in_where, in_group_by, in_aggregate, in_order_by
                    ),
                )
                for val in node.expressions:
                    rt = cast(
                        DataType,
                        self._validate_expression(
                            val, scope, in_where, in_group_by, in_aggregate, in_order_by
                        ),
                    )
                    self._assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Paren():
                return self._validate_expression(
                    node.this, scope, in_where, in_group_by, in_aggregate, in_order_by
                )

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    # ──────── Aggregate Validations ────────

    def _validate_aggregate(self, in_where: bool, in_aggregate: bool) -> None:
        if in_where:
            raise AggregateInWhereError()
        if in_aggregate:
            raise NestedAggregateError()

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
