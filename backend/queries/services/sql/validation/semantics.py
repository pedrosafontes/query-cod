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
    All,
    And,
    Any,
    Avg,
    Boolean,
    Column,
    Count,
    Div,
    Except,
    Exists,
    From,
    Identifier,
    In,
    Intersect,
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
    Union,
)

from .context import ValidationContext
from .errors import (
    AggregateInWhereError,
    ColumnCountMismatchError,
    ColumnTypeMismatchError,
    CrossJoinConditionError,
    DerivedColumnAliasRequiredError,
    DerivedTableMultipleSchemasError,
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
)
from .scope import Scope
from .scope.projection_scope import ProjectionScope
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
        self._validate_query(expression, outer_scope=None)

    def _validate_query(self, query: Expression, outer_scope: Scope | None) -> ResultSchema:
        match query:
            case Select():
                return self._validate_select(query, outer_scope)
            case Union() | Intersect() | Except():
                return self._validate_set_operation(query, outer_scope)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')

    def _validate_set_operation(
        self, query: Union | Intersect | Except, outer_scope: Scope | None
    ) -> ResultSchema:
        left_schema = self._validate_query(query.left, outer_scope)
        right_schema = self._validate_query(query.right, outer_scope)

        left_types = ProjectionScope.flatten_result_schema(left_schema)
        right_types = ProjectionScope.flatten_result_schema(right_schema)

        if (l_len := len(left_types)) != (r_len := len(right_types)):
            raise ColumnCountMismatchError(l_len, r_len)

        for i, (lt, rt) in enumerate(zip(left_types, right_types, strict=False)):
            try:
                assert_comparable(lt, rt)
            except TypeMismatchError:
                raise ColumnTypeMismatchError(lt, rt, i) from None

        return left_schema

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
        if from_clause:
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
                scope.group_by.add(
                    expr,
                    self._validate_simple_expression(
                        expr, scope, ValidationContext(in_group_by=True)
                    ),
                )

    def _validate_having(self, select: Select, scope: Scope) -> None:
        having = select.args.get('having')
        if having:
            assert_boolean(
                self._validate_simple_expression(
                    having.this, scope, ValidationContext(in_having=True)
                )
            )

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
                scope.projections.add(expr, t)
            else:
                # Projection contains star expansion
                for table, columns in cast(ResultSchema, t).items():
                    for col, col_type in columns.items():
                        scope.projections.add(Column(this=col, table=table), col_type)

    def _validate_order_by(self, select: Select, scope: Scope) -> None:
        order = select.args.get('order')
        if not order:
            return

        num_projections = len(scope.projections.expressions)
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
                t = scope.projections.resolve(node)
                if t is None:
                    raise OrderByExpressionError(node)
            else:
                t = self._validate_simple_expression(
                    node, scope, ValidationContext(in_order_by=True)
                )
            assert_orderable(t)

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
                scope.tables.add(alias, table_schema)

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
                try:
                    [(_, sub_schema)] = self._validate_query(sub_select, scope).items()
                except ValueError:  # Unpack error
                    # Derived tables must return a single table
                    raise DerivedTableMultipleSchemasError() from None
                scope.tables.add(alias, sub_schema)

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

                    if (
                        # If the query is grouped, the column must be in the GROUP BY clause or appear in an aggregate function
                        # Validates HAVING, SELECT, and ORDER BY (occur after GROUP BY)
                        scope.is_grouped
                        and not context.in_group_by  # Still in the GROUP BY clause
                        and not (scope.group_by.contains(node) or context.in_aggregate)
                    ) or (
                        # If the query is not grouped, columns in the HAVING clause must appear in an aggregate function
                        not scope.is_grouped and context.in_having and not context.in_aggregate
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
                sub_schema = self._validate_query(node.this, scope)
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
                if subquery := node.args.get('query'):
                    rt = self._validate_quantified_predicate_query(subquery.this, scope)
                    assert_comparable(lt, rt)
                else:
                    # If the IN clause is not a subquery, it must be a list of literals
                    for val in node.expressions:
                        rt = self._validate_simple_expression(val, scope, context)
                        assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Any() | All():
                query_expr = node.this
                if isinstance(query_expr, Subquery):
                    # Unwrap the subquery
                    query_expr = query_expr.this
                return self._validate_quantified_predicate_query(query_expr, scope)

            case Exists():
                self._validate_query(node.this, scope)
                return DataType.BOOLEAN

            case Paren():
                return self._validate_expression(node.this, scope, context)

            case Boolean():
                return DataType.BOOLEAN

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

    # ──────── Quantified Predicate Validations ────────

    def _validate_quantified_predicate_query(self, query: Expression, scope: Scope) -> DataType:
        schema = self._validate_query(query, scope)
        try:
            [(_, columns)] = schema.items()
            [(_, rt)] = columns.items()
        except ValueError:  # Unpack error
            raise ColumnCountMismatchError(1, len(columns)) from None
        return rt
