from databases.types import DataType, Schema
from sqlglot import Expression
from sqlglot.expressions import (
    Avg,
    Binary,
    Column,
    Count,
    From,
    Join,
    Literal,
    Max,
    Min,
    Not,
    Select,
    Star,
    Sum,
    Table,
)

from .errors import (
    GroupByError,
    OrderByExpressionError,
    OrderByPositionError,
    SQLSemanticError,
    TypeMismatchError,
    UndefinedTableError,
)
from .types import Scope
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
        if where := select.args.get('where'):
            self._validate_expression(where.this, scope)

        # 4. GROUP BY - validate grouping expressions
        if group := select.args.get('group'):
            for exp in group.expressions:
                self._validate_expression(exp, scope)
                scope.group_by_cols.add(exp.name)

        # 5. HAVING - validate having expressions
        if having := select.args.get('having'):
            if not scope.group_by_cols:
                raise SQLSemanticError('HAVING clause without GROUP BY')
            self._validate_expression(having.this, scope)

        # 6. SELECT - validate select expressions
        for proj in select.expressions:
            self._validate_expression(proj, scope)

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
                    if exp not in select.expressions:
                        raise OrderByExpressionError(exp)
                else:
                    self._validate_expression(exp, scope)

    def _populate_from_scope(self, select: Select, scope: Scope) -> None:
        from_clause = select.args.get('from')
        if not isinstance(from_clause, From):
            return

        self._validate_table_reference(from_clause.this, scope)

    def _validate_joins(self, select: Select, scope: Scope) -> None:
        for join in select.args.get('joins', []):
            assert isinstance(join, Join)  # noqa S101
            self._validate_table_reference(join.this, scope)

            # Validate JOIN condition
            if condition := join.args.get('on'):
                self._validate_expression(condition, scope)

    def _validate_table_reference(self, table_ref: Table, scope: Scope) -> None:
        match table_ref:
            case Table():
                table_name = table_ref.name
                alias = table_ref.alias_or_name
                schema_entry = self.schema.get(table_name)
                if schema_entry is None:
                    raise UndefinedTableError(table_name)
                scope.tables[alias] = table_name
                for col, dtype in schema_entry.items():
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
        in_aggregate: bool = False,
    ) -> DataType:
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                col_t = scope.resolve_column(node)
                if (
                    not in_aggregate
                    and scope.group_by_cols
                    and node.name not in scope.group_by_cols
                ):
                    raise GroupByError(node.name)
                return col_t

            case Binary():
                left_t = self._validate_expression(node.left, scope, in_aggregate)
                right_t = self._validate_expression(node.right, scope, in_aggregate)
                if not left_t.is_comparable_with(right_t):
                    raise TypeMismatchError(left_t, right_t)
                return DataType.BOOLEAN

            case Not():
                if (
                    not_t := self._validate_expression(node.this, scope, in_aggregate)
                ) != DataType.BOOLEAN:
                    raise TypeMismatchError(DataType.BOOLEAN, not_t)

                return DataType.BOOLEAN

            case Count():
                arg = node.this
                if not isinstance(arg, Star):
                    self._validate_expression(arg, scope, in_aggregate=True)
                return DataType.INTEGER

            case Avg() | Sum() | Min() | Max():
                arg = node.this
                if not self._validate_expression(arg, scope, in_aggregate=True).is_numeric():
                    raise TypeMismatchError(DataType.NUMERIC, arg)
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
