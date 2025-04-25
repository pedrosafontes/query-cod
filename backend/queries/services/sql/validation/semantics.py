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

from .context import ValidationContext
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
    UndefinedColumnError,
    UndefinedTableError,
)
from .scope import Scope
from .type_checker import (
    assert_boolean,
    assert_comparable,
    assert_integer_literal,
    assert_numeric,
    assert_orderable,
    assert_scalar_subquery,
    infer_literal_type,
)
from .types import ColumnTypes, ResultSchema


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, expression: Select) -> None:
        self._validate_select(expression, outer_scope=None)

    def _validate_select(self, select: Select, outer_scope: Scope | None) -> ResultSchema:
        # Validate all clauses of a SELECT statement in the order of execution
        scope = Scope(outer_scope)
        self._populate_from(select, scope)
        self._validate_joins(select, scope)
        self._validate_where(select, scope)
        self._validate_group_by(select, scope)
        self._validate_having(select, scope)
        self._validate_projection(select, scope)
        self._validate_order_by(select, scope)
        return scope.projections.schema

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

            left_cols = scope.tables.snapshot_columns()
            self._add_table(join.this, scope)
            right_cols = self.schema[join.this.name]

            kind = join.method or join.args.get('kind', 'INNER')
            using = join.args.get('using')
            condition = join.args.get('on')

            if using:
                self._validate_using(using, left_cols, right_cols)
            elif kind == 'NATURAL':
                self._validate_natural_join(left_cols, right_cols)
            elif kind == 'CROSS':
                # CROSS JOINS must not have a condition
                if condition:
                    raise CrossJoinConditionError()
            else:
                # INNER, LEFT, RIGHT, and FULL OUTER joins must have a condition
                if not condition:
                    raise MissingJoinConditionError()
                assert_boolean(self._validate_simple_expression(condition, scope))

    def _validate_where(self, select: Select, scope: Scope) -> None:
        where = select.args.get('where')
        if where:
            assert_boolean(
                self._validate_simple_expression(
                    where.this, scope, ValidationContext(in_where=True)
                )
            )

    def _validate_group_by(self, select: Select, scope: Scope) -> None:
        group = select.args.get('group')
        if group:
            # Validate GROUP BY expressions
            for expr in group.expressions:
                scope.group_by.add_expr(
                    expr,
                    self._validate_simple_expression(
                        expr, scope, ValidationContext(in_group_by=True)
                    ),
                )

    def _validate_having(self, select: Select, scope: Scope) -> None:
        having = select.args.get('having')
        if having:
            if not scope.is_grouped:
                # If there is a HAVING clause, there must be a GROUP BY clause
                raise GroupByClauseRequiredError()
            assert_boolean(self._validate_simple_expression(having.this, scope))

    def _validate_projection(self, select: Select, scope: Scope) -> None:
        for expr in select.expressions:
            t = (
                scope.group_by.type_of(
                    expr
                )  # Expression has already been validated if it is in group by
                if scope.group_by.contains(expr)
                else self._validate_expression(expr, scope)
            )
            if isinstance(t, DataType):
                # Projection is a single column or expression
                scope.projections.add(expr.args.get('table'), expr.alias_or_name, t)
            else:
                # Projection contains star expansion
                for table, columns in cast(ResultSchema, t).items():
                    for col, col_type in columns.items():
                        scope.projections.add(table, col, col_type)

    def _validate_order_by(self, select: Select, scope: Scope) -> None:
        order = select.args.get('order')
        if not order:
            return

        num_projections = len(select.expressions)
        for item in order.expressions:
            node = item.this
            if isinstance(node, Literal):
                # Positional ordering must be an integer literal in the range of projections
                assert_integer_literal(node)
                pos = int(node.this)
                if not (1 <= pos <= num_projections):
                    raise OrderByPositionError(1, num_projections)
                continue

            if scope.is_grouped:
                if not (node in select.expressions or scope.projections.contains(node)):
                    raise OrderByExpressionError(node)
            else:
                assert_orderable(
                    self._validate_simple_expression(
                        node, scope, ValidationContext(in_order_by=True)
                    ),
                )

    # ──────── Join Helpers ────────

    def _validate_using(
        self, using: list[Identifier], left: ColumnTypes, right: TableSchema
    ) -> None:
        # All columns in USING must be present in both tables
        for ident in using:
            col = ident.name
            if col not in left:
                raise UndefinedColumnError(col)
            for ltype in left[col]:
                assert_comparable(ltype, right[col])

    def _validate_natural_join(self, left: ColumnTypes, right: TableSchema) -> None:
        shared = set(left) & set(right)
        # NATURAL JOIN must have at least one common column
        if not shared:
            raise NoCommonColumnsError()
        # All common columns must be comparable
        for col in shared:
            for ltype in left[col]:
                assert_comparable(ltype, right[col])

    # ──────── Table & Expression Validation ────────

    def _add_table(self, table: Table | Subquery, scope: Scope) -> None:
        match table:
            case Table():
                name = table.name
                alias = table.alias_or_name
                table_schema = self.schema.get(name)
                if table_schema is None:
                    raise UndefinedTableError(name)
                scope.tables.register(alias, table_schema)

            case Subquery():
                alias = table.alias_or_name
                # Derived tables must have an alias
                if not alias:
                    raise MissingDerivedTableAliasError()
                sub_select = table.this
                for expr in sub_select.expressions:
                    # Derived columns must have an alias
                    if not expr.alias_or_name:
                        raise DerivedColumnAliasRequiredError(expr)
                [(_, sub_schema)] = self._validate_select(sub_select, scope).items()
                scope.tables.register(alias, sub_schema)

    def _validate_simple_expression(
        self,
        node: Expression,
        scope: Scope,
        context: ValidationContext | None = None,
    ) -> DataType:
        return cast(DataType, self._validate_expression(node, scope, context))

    def _validate_expression(
        self,
        node: Expression,
        scope: Scope,
        context: ValidationContext | None = None,
    ) -> DataType | ResultSchema:
        if context is None:
            context = ValidationContext()
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                if isinstance(node.this, Star):
                    return scope.validate_star_expansion(node.table)
                else:
                    t = scope.resolve_column(node, context.in_order_by)
                    # If the query is grouped, the column must be in the GROUP BY clause or appear in an aggregate function
                    if (
                        scope.is_grouped
                        and not context.in_group_by  # Still in the GROUP BY clause
                        and not (scope.group_by.contains(node) or context.in_aggregate)
                    ):
                        raise NonGroupedColumnError([node.name])
                    return t

            case Alias():
                return self._validate_expression(node.this, scope, context)

            case And() | Or():
                lt = self._validate_simple_expression(node.left, scope, context)
                rt = self._validate_simple_expression(node.right, scope, context)
                assert_boolean(lt)
                assert_boolean(rt)
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                lt = self._validate_simple_expression(node.left, scope, context)
                rt = self._validate_simple_expression(node.right, scope, context)
                assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Add() | Sub() | Mul() | Div():
                lt = self._validate_simple_expression(node.left, scope, context)
                rt = self._validate_simple_expression(node.right, scope, context)
                assert_numeric(lt)
                assert_numeric(rt)
                return DataType.NUMERIC

            case Not():
                assert_boolean(self._validate_simple_expression(node.this, scope, context))
                return DataType.BOOLEAN

            case Count():
                self._validate_aggregate(context)
                arg = node.this
                if not isinstance(arg, Star):
                    self._validate_expression(arg, scope, context.enter_aggregate())
                return DataType.INTEGER

            case Avg() | Sum():
                self._validate_aggregate(context)
                assert_numeric(
                    self._validate_simple_expression(node.this, scope, context.enter_aggregate())
                )
                return DataType.NUMERIC

            case Min() | Max():
                self._validate_aggregate(context)
                t = self._validate_simple_expression(node.this, scope, context.enter_aggregate())
                assert_orderable(t)
                return t

            case Star():
                return scope.validate_star_expansion()

            case Subquery():
                sub_schema = self._validate_select(node.this, scope)
                try:
                    assert_scalar_subquery(node)
                    [(_, columns)] = sub_schema.items()
                    [(_, t)] = columns.items()
                except ValueError:  # Unpack error
                    # Subquery must return a single table with a single column
                    raise ScalarSubqueryError() from None
                return t

            case In():
                lt = self._validate_simple_expression(node.this, scope, context)
                for val in node.expressions:
                    rt = self._validate_simple_expression(val, scope, context)
                    assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Paren():
                return self._validate_expression(node.this, scope, context)

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    # ──────── Aggregate Validations ────────

    def _validate_aggregate(self, context: ValidationContext) -> None:
        # Cannot be used in the WHERE clause
        if context.in_where:
            raise AggregateInWhereError()
        # Cannot be nested
        if context.in_aggregate:
            raise NestedAggregateError()
