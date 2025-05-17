from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonOperator,
    ComparisonValue,
    NotExpression,
)
from sqlglot.expressions import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    And,
    Boolean,
    Column,
    Expression,
    Literal,
    Not,
    Or,
    Paren,
)

from ..semantics.types import (
    BooleanExpression as SQLBooleanExpression,
)
from ..semantics.types import (
    Comparison as SQLComparison,
)


class ExpressionTranspiler:
    def transpile(
        self,
        expr: Expression,
    ) -> BooleanExpression:
        match expr:
            case Column():
                return self.transpile_column(expr)

            case Paren():
                return self.transpile(expr.this)

            # Comparison
            case comp if isinstance(comp, SQLComparison):
                return self._transpile_comparison(comp)

            # Predicates
            case expr if isinstance(expr, SQLBooleanExpression):
                return self._transpile_boolean_expr(expr)

            case _:
                raise NotImplementedError(f'Expression {type(expr)} not supported')

    def transpile_column(
        self,
        expr: Column,
    ) -> Attribute:
        return Attribute(name=str(expr.this), relation=expr.table or None)

    def _transpile_value(
        self,
        value: Expression,
    ) -> ComparisonValue:
        match value:
            case Column():
                return self.transpile_column(value)
            case Literal():
                if value.is_string:
                    return str(value.this)
                elif value.is_number:
                    return float(value.this)
                else:
                    raise NotImplementedError(f'Literal type {type(value)} not supported')
            case Boolean():
                return bool(value.this)
            case _:
                raise NotImplementedError(f'Value {type(value)} not supported')

    def _transpile_comparison(self, comp: SQLComparison) -> Comparison:
        operator: ComparisonOperator
        match comp:
            case EQ():
                operator = ComparisonOperator.EQUAL
            case NEQ():
                operator = ComparisonOperator.NOT_EQUAL
            case GT():
                operator = ComparisonOperator.GREATER_THAN
            case GTE():
                operator = ComparisonOperator.GREATER_THAN_EQUAL
            case LT():
                operator = ComparisonOperator.LESS_THAN
            case LTE():
                operator = ComparisonOperator.LESS_THAN_EQUAL
        return Comparison(
            operator=operator,
            left=self._transpile_value(comp.left),
            right=self._transpile_value(comp.right),
        )

    # # ──────── Predicate Expressions ────────
    def _transpile_boolean_expr(
        self,
        expr: SQLBooleanExpression,
    ) -> BooleanExpression:
        match expr:
            case And():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.AND,
                    left=self.transpile(expr.left),
                    right=self.transpile(expr.right),
                )

            case Or():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.OR,
                    left=self.transpile(expr.left),
                    right=self.transpile(expr.right),
                )

            case Not():
                return NotExpression(
                    expression=self.transpile(expr.this),
                )
