from typing import cast

from queries.services.types import RelationalSchema
from sqlglot.expressions import (
    Column,
    Expression,
    From,
    Join,
    Select,
)

from ..context import ValidationContext
from ..inferrer import TypeInferrer
from ..scope import Scope
from .expression import ExpressionValidator
from .join import JoinValidator
from .order_by import OrderByValidator
from .table import TableValidator


class SelectValidator:
    def __init__(self, schema: RelationalSchema, scope: Scope) -> None:
        self.schema = schema
        self.scope = scope
        self.expr_validator = ExpressionValidator(schema, scope)
        self.table_validator = TableValidator(schema, scope)
        self.join_validator = JoinValidator(
            schema, scope, self.expr_validator, self.table_validator
        )
        self.order_by_validator = OrderByValidator(self.scope, self.expr_validator)
        self._type_inferrer = TypeInferrer(self.scope)

    def validate(self, select: Select) -> None:
        self.process_from(select)
        self.validate_joins(select)
        self.validate_where(select)
        self.process_group_by(select)
        self.validate_having(select)
        self.validate_projection(select)
        self.validate_order_by(select)

    def process_from(self, select: Select) -> None:
        from_clause: From | None = select.args.get('from')
        if from_clause:
            schema = self.table_validator.validate(from_clause.this)
            self.scope.tables.add(from_clause.this, schema)

    def validate_joins(self, select: Select) -> None:
        joins: list[Join] = select.args.get('joins', [])
        for join in joins:
            self.join_validator.validate_join(join)

    def validate_where(self, select: Select) -> None:
        where: Expression | None = select.args.get('where')
        if where:
            self.expr_validator._validate_boolean(where.this, ValidationContext(in_where=True))

    def process_group_by(self, select: Select) -> None:
        group = select.args.get('group')
        if group:
            expressions: list[Expression] = group.expressions
            self.scope.group_by.add(expressions)
            # Validate GROUP BY expressions
            for expr in expressions:
                self.expr_validator.validate_expression(expr, ValidationContext(in_group_by=True))

    def validate_having(self, select: Select) -> None:
        having: Expression | None = select.args.get('having')
        if having:
            self.expr_validator._validate_boolean(having.this, ValidationContext(in_having=True))

    def validate_projection(self, select: Select) -> None:
        for expr in cast(list[Expression], select.expressions):
            inner = expr.unalias()
            if inner.is_star:
                schema = self.expr_validator.validate_star(inner)
                for table, columns in schema.items():
                    for col, col_type in columns.items():
                        self.scope.projections.add(Column(this=col, table=table), col_type)
            else:
                if not self.scope.group_by.contains(inner):
                    self.expr_validator.validate_expression(inner)
                self.scope.projections.add(expr, self._type_inferrer.infer(expr))

    def validate_order_by(self, select: Select) -> None:
        order = select.args.get('order')
        if order:
            self.order_by_validator.validate(order.expressions)
