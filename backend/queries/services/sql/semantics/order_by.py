from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Expression, Literal

from ..inference import TypeInferrer
from ..scope import SelectScope
from .errors import OrderByExpressionError, OrderByPositionError, TypeMismatchError
from .expression import ExpressionValidator
from .utils import is_aggregate


class OrderByValidator:
    def __init__(self, scope: SelectScope, expr_validator: ExpressionValidator):
        self.scope = scope
        self.expr_validator = expr_validator
        self.type_inferrer = TypeInferrer(scope)

    def validate(self, order_by_expressions: list[Expression]) -> None:
        for item in order_by_expressions:
            node = item.this
            if isinstance(node, Literal):
                self._validate_position(node)
            else:
                self._validate_expression(node)

    def _validate_position(self, node: Literal) -> None:
        expected_type = DataType.INTEGER
        literal_type = self.type_inferrer.infer(node)
        if literal_type != expected_type:
            raise TypeMismatchError(node, expected_type, literal_type)

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
