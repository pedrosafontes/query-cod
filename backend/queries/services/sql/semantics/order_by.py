from query_cod.types import DataType
from sqlglot.expressions import Expression, Literal, Ordered

from ..inference import TypeInferrer
from ..scope import SelectScope
from .context import ValidationContext
from .errors import OrderByPositionError, TypeMismatchError
from .expression import ExpressionValidator


class OrderByValidator:
    def __init__(self, scope: SelectScope):
        self.scope = scope
        self.max_position = len(scope.projections.expressions)
        self.expr_validator = ExpressionValidator(scope)
        self._type_inferrer = TypeInferrer(scope)

    def validate(self, expr: Ordered) -> None:
        inner = expr.this
        if isinstance(inner, Literal):
            self._validate_position(inner)
        else:
            self._validate_expression(inner)

    def _validate_position(self, literal: Literal) -> None:
        # Check if the literal is a valid integer
        expected_t = DataType.INTEGER
        actual_t = self._type_inferrer.infer(literal)
        if actual_t != expected_t:
            raise TypeMismatchError(literal, expected_t, actual_t)

        # Check if the position is within the valid range
        pos = int(literal.this)
        if not (1 <= pos <= self.max_position):
            raise OrderByPositionError(literal, self.max_position)

    def _validate_expression(self, expr: Expression) -> None:
        if expr in self.scope.projections or expr in self.scope.group_by:
            # Ordering by a projection is valid
            return

        self.expr_validator.validate(expr, ValidationContext(in_order_by=True))
