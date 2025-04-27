from typing import cast

from databases.types import Schema
from queries.services.types import ResultSchema
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import (
    Column,
    From,
    Join,
    Literal,
    Select,
)

from ..context import ValidationContext
from ..errors import OrderByExpressionError, OrderByPositionError
from ..scope import Scope
from ..type_utils import assert_boolean, assert_integer_literal, assert_orderable, is_aggregate
from .expression import ExpressionValidator
from .join import JoinValidator
from .table import TableValidator


class ClauseValidator:
    def __init__(self, schema: Schema, scope: Scope) -> None:
        self.schema = schema
        self.scope = scope
        self.expr_validator = ExpressionValidator(schema, scope)
        self.table_validator = TableValidator(schema, scope)
        self.join_validator = JoinValidator(
            schema, scope, self.expr_validator, self.table_validator
        )

    def process_from(self, select: Select) -> None:
        from_clause = select.args.get('from')
        if from_clause:
            if not isinstance(from_clause, From):
                raise NotImplementedError(f'Unsupported FROM clause: {type(from_clause)}')
            alias, schema = self.table_validator.validate(from_clause.this)
            self.scope.tables.add(alias, schema)

    def validate_joins(self, select: Select) -> None:
        for join in select.args.get('joins', []):
            if not isinstance(join, Join):
                raise NotImplementedError(f'Unsupported join type: {type(join)}')
            self.join_validator.validate_join(join)

    def validate_where(self, select: Select) -> None:
        where = select.args.get('where')
        if where:
            assert_boolean(
                self.expr_validator.validate_basic(where.this, ValidationContext(in_where=True))
            )

    def validate_group_by(self, select: Select) -> None:
        group = select.args.get('group')
        if group:
            # Validate GROUP BY expressions
            for expr in group.expressions:
                self.scope.group_by.add(
                    expr,
                    self.expr_validator.validate_basic(expr, ValidationContext(in_group_by=True)),
                )

    def validate_having(self, select: Select) -> None:
        having = select.args.get('having')
        if having:
            assert_boolean(
                self.expr_validator.validate_basic(having.this, ValidationContext(in_having=True))
            )

    def validate_projection(self, select: Select) -> None:
        for expr in select.expressions:
            t = (
                self.scope.group_by.resolve(
                    expr
                )  # Expression has already been validated if it is in group by
                if self.scope.group_by.contains(expr)
                else self.expr_validator.validate(expr)
            )
            if isinstance(t, DataType):
                # Projection is a single column or expression
                self.scope.projections.add(expr, t)
            else:
                # Projection contains star expansion
                for table, columns in cast(ResultSchema, t).items():
                    for col, col_type in columns.items():
                        self.scope.projections.add(Column(this=col, table=table), col_type)

    def validate_order_by(self, select: Select) -> None:
        order = select.args.get('order')
        if not order:
            return

        num_projections = len(self.scope.projections.expressions)
        for item in order.expressions:
            node = item.this
            if isinstance(node, Literal):
                # Positional ordering must be an integer literal in the range of projections
                assert_integer_literal(node)
                pos = int(node.this)
                if not (1 <= pos <= num_projections):
                    raise OrderByPositionError(1, num_projections)
                continue

            if self.scope.is_grouped:
                t: DataType | None = (
                    self.scope.projections.resolve(node)
                    or self.scope.group_by.resolve(node)
                    or (is_aggregate(node) and self.expr_validator.validate_basic(node))
                    or None
                )
                if t is None:
                    raise OrderByExpressionError(node)
            else:
                t = self.scope.projections.resolve(node) or self.expr_validator.validate_basic(node)
            assert_orderable(t)
