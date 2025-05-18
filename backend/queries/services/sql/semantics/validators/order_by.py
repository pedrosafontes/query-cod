from sqlglot.expressions import Expression, Literal

from ..errors import OrderByExpressionError, OrderByPositionError
from ..scope import Scope
from ..utils import assert_integer_literal, is_aggregate
from .expression import ExpressionValidator


class OrderByValidator:
    def __init__(self, scope: Scope, expr_validator: ExpressionValidator):
        self.scope = scope
        self.expr_validator = expr_validator

    def validate(self, order_by_expressions: list[Expression]) -> None:
        for item in order_by_expressions:
            node = item.this
            if isinstance(node, Literal):
                self._validate_position(node)
            else:
                self._validate_expression(node)

    def _validate_position(self, node: Literal) -> None:
        assert_integer_literal(node)
        pos = int(node.this)
        num_projections = len(self.scope.projections.expressions)
        if not (1 <= pos <= num_projections):
            raise OrderByPositionError(node, 1, num_projections)

    def _validate_expression(self, node: Expression) -> None:
        if self.scope.projections.contains(node):
            return

        if self.scope.is_grouped:
            if self.scope.group_by.contains(node):
                return
            if is_aggregate(node):
                self.expr_validator.validate_expression(node)
            else:
                raise OrderByExpressionError(node)
        else:
            self.expr_validator.validate_expression(node)
