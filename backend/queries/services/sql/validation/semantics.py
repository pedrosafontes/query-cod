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
    Sum,
    Table,
)

from .errors import (
    GroupByError,
    MissingJoinConditionError,
    OrderByExpressionError,
    OrderByPositionError,
    SQLSemanticError,
    TypeMismatchError,
    UndefinedColumnError,
    UndefinedTableError,
    UnorderableTypeError,
)
from .types import ColumnBindingsMap, Scope
from .utils import infer_literal_type


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, expression: Select) -> None:
        self._validate_query(expression)

    def _validate_query(self, expression: Select, scope: Scope | None = None) -> None:
        self._validate_select(expression, scope)

    def _validate_select(self, select: Select, outer_scope: Scope | None) -> None:
        scope = Scope(outer_scope)
        # 1. FROM clause - validate tables & populate scope
        self._populate_from_scope(select, scope)

        # 2. JOIN clause - validate joins & populate scope
        self._validate_joins(select, scope)

        # 3. WHERE - validate filter expressions
        if (where := select.args.get('where')) and (
            predicate_t := self._validate_expression(where.this, scope)
        ) != DataType.BOOLEAN:
            raise TypeMismatchError(DataType.BOOLEAN, predicate_t)

        # 4. GROUP BY - validate grouping expressions
        if group := select.args.get('group'):
            for exp in group.expressions:
                self._validate_expression(exp, scope, in_group_by=True)
                scope.group_by_cols.add(exp.name)

        # 5. HAVING - validate having expressions
        if having := select.args.get('having'):
            if not scope.group_by_cols:
                raise SQLSemanticError('HAVING clause without GROUP BY')
            if (predicate_t := self._validate_expression(having.this, scope)) != DataType.BOOLEAN:
                raise TypeMismatchError(DataType.BOOLEAN, predicate_t)

        # 6. SELECT - validate select expressions
        for proj in select.expressions:
            self._validate_expression(proj, scope)
            scope.add_select_item(proj)

        # 7. ORDER BY - validate order expressions
        if order := select.args.get('order'):
            for ordered in order.expressions:
                exp = ordered.this
                if isinstance(exp, Literal):
                    if not exp.is_int:
                        raise TypeMismatchError(DataType.INTEGER, infer_literal_type(exp))

                    num_projections = len(select.expressions)
                    if not (1 <= int(exp.this) <= num_projections):
                        raise OrderByPositionError(1, num_projections)
                if scope.group_by_cols:
                    if exp not in select.expressions and exp.name not in scope.select_items:
                        raise OrderByExpressionError(exp)
                else:
                    if not (order_t := self._validate_expression(exp, scope)).is_orderable():
                        raise UnorderableTypeError(order_t)

    def _populate_from_scope(self, select: Select, scope: Scope) -> None:
        from_clause = select.args.get('from')
        if not isinstance(from_clause, From):
            raise NotImplementedError(
                f'FROM clause type {type(from_clause)} is not supported for validation'
            )
        self._validate_table_reference(from_clause.this, scope)

    def _validate_joins(self, select: Select, scope: Scope) -> None:
        for join in select.args.get('joins', []):
            assert isinstance(join, Join) # noqa S101
            left_cols = scope.columns.copy()
            self._validate_table_reference(join.this, scope)
            right_cols = self.schema[join.this.name]

            kind, using, condition = (
                join.method or join.args.get('kind'),
                join.args.get('using'),
                join.args.get('on'),
            )

            if using:
                self._validate_using(using, left_cols, right_cols)
            elif kind == 'NATURAL':
                self._validate_natural_join(left_cols, right_cols, scope)
            elif kind == 'CROSS':
                if join.args.get('on'):
                    raise SQLSemanticError('CROSS JOIN cannot have an ON clause')
            else:
                if not condition:
                    raise MissingJoinConditionError()
                cond_t = self._validate_expression(condition, scope)
                if cond_t != DataType.BOOLEAN:
                    raise TypeMismatchError(DataType.BOOLEAN, cond_t)

    def _validate_using(
        self, using: list[Identifier], left_cols: ColumnBindingsMap, right_cols: TableSchema
    ) -> None:
        for ident in using:
            col = ident.name

            if not left_cols[col]:
                raise UndefinedColumnError(col)

            rhs_dtype = right_cols[col]
            for _, lhs_dtype in left_cols[col]:
                if not lhs_dtype.is_comparable_with(rhs_dtype):
                    raise TypeMismatchError(lhs_dtype, rhs_dtype)

    def _validate_natural_join(
        self, left_cols: ColumnBindingsMap, right_cols: TableSchema, scope: Scope
    ) -> None:
        shared = set(right_cols.keys()) & set(left_cols.keys())

        if not shared:
            raise SQLSemanticError('NATURAL JOIN has no common columns')

        for col in shared:
            rhs_dtype = right_cols[col]
            for _, lhs_dtype in scope.columns[col]:
                if not lhs_dtype.is_comparable_with(rhs_dtype):
                    raise TypeMismatchError(lhs_dtype, rhs_dtype)

    def _validate_table_reference(self, table_ref: Table, scope: Scope) -> None:
        match table_ref:
            case Table():
                table_name = table_ref.name
                alias = table_ref.alias_or_name
                table_schema = self.schema.get(table_name)
                if table_schema is None:
                    raise UndefinedTableError(table_name)
                scope.add_table(alias, table_name)
                for col, dtype in table_schema.items():
                    scope.add_column(alias, col, dtype)

            case _:
                # TODO: Check for other table types
                raise NotImplementedError(
                    f'Table reference type {type(table_ref)} is not supported for validation'
                )

    def _validate_expression(
        self,
        node: Expression,
        scope: Scope,
        in_group_by: bool = False,
        in_aggregate: bool = False,
    ) -> DataType:
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                col_t = scope.resolve_column(node)
                if (
                    not in_group_by
                    and not in_aggregate
                    and scope.group_by_cols
                    and node.name not in scope.group_by_cols
                ):
                    raise GroupByError(node.name)
                return col_t

            case Alias():
                return self._validate_expression(node.this, scope, in_group_by, in_aggregate)

            case And() | Or():
                left_t = self._validate_expression(node.left, scope, in_group_by, in_aggregate)
                right_t = self._validate_expression(node.right, scope, in_group_by, in_aggregate)
                if left_t is not DataType.BOOLEAN or right_t is not DataType.BOOLEAN:
                    raise TypeMismatchError(
                        DataType.BOOLEAN, left_t if left_t is not DataType.BOOLEAN else right_t
                    )
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                left_t = self._validate_expression(node.left, scope, in_group_by, in_aggregate)
                right_t = self._validate_expression(node.right, scope, in_group_by, in_aggregate)
                if not left_t.is_comparable_with(right_t):
                    raise TypeMismatchError(left_t, right_t)
                return DataType.BOOLEAN

            case Add() | Sub() | Mul() | Div():
                left_t = self._validate_expression(node.left, scope, in_group_by, in_aggregate)
                right_t = self._validate_expression(node.right, scope, in_group_by, in_aggregate)
                if not (left_t.is_numeric() and right_t.is_numeric()):
                    raise TypeMismatchError(
                        DataType.NUMERIC, left_t if not left_t.is_numeric() else right_t
                    )
                return DataType.NUMERIC

            case Not():
                if (
                    not_t := self._validate_expression(node.this, scope, in_group_by, in_aggregate)
                ) != DataType.BOOLEAN:
                    raise TypeMismatchError(DataType.BOOLEAN, not_t)

                return DataType.BOOLEAN

            case Count():
                arg = node.this
                if not isinstance(arg, Star):
                    self._validate_expression(arg, scope, in_aggregate=True)
                return DataType.INTEGER

            case Avg() | Sum() | Min() | Max():
                arg_t = self._validate_expression(node.this, scope, in_aggregate=True)
                if not arg_t.is_numeric():
                    raise TypeMismatchError(DataType.NUMERIC, arg_t)
                return DataType.NUMERIC

            case Star():
                if scope.group_by_cols and scope.columns.keys() != scope.group_by_cols:
                    raise SQLSemanticError()
                return None
            case _:
                # TODO: Handle other expression types
                raise NotImplementedError(
                    f'Expression type {type(node)} is not supported for validation'
                )
