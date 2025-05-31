from collections.abc import Callable

from queries.services.types import SQLQuery
from query_cod.types import DataType
from sqlglot import Expression
from sqlglot import expressions as exp

from ..inference import TypeInferrer
from ..scope import SelectScope
from ..types import (
    AggregateFunction,
    ArithmeticOperation,
    BooleanExpression,
    Comparison,
    StringOperation,
)
from ..utils import convert_sqlglot_type
from .context import ValidationContext
from .errors import (
    AggregateInWhereError,
    ArithmeticTypeMismatchError,
    ColumnCountMismatchError,
    ColumnNotFoundError,
    InvalidCastError,
    NestedAggregateError,
    UngroupedColumnError,
)
from .errors.data_type import NonScalarExpressionError
from .utils import (
    assert_boolean,
    assert_comparable,
    assert_numeric,
    assert_string,
    is_aggregate,
)


class ExpressionValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope
        self._type_inferrer = TypeInferrer(scope)

    def validate(
        self,
        expr: Expression,
        context: ValidationContext | None = None,
    ) -> None:
        from .query import validate_query

        if context is None:
            # Create a new context if not provided
            context = ValidationContext()

        match expr:
            case exp.Column():
                self._validate_column(expr, context)

            case exp.Subquery():
                self._validate_scalar_subquery(expr)

            case exp.Alias() | exp.Paren() | exp.Is():
                self.validate(expr.this, context)

            case exp.Distinct():
                [expression] = expr.expressions
                self.validate(expression, context)

            case comp if isinstance(comp, Comparison):
                self._validate_comparison(comp, context)

            case op if isinstance(op, ArithmeticOperation):
                self._validate_arithmetic_operation(expr, context)

            case aggr if isinstance(aggr, AggregateFunction):
                self._validate_aggregate(aggr, context)

            case op if isinstance(op, StringOperation):
                self._validate_string_operation(op, context)

            case exp.Cast():
                self._validate_cast(expr, context)

            case expr if isinstance(expr, BooleanExpression):
                self._validate_boolean_expr(expr, context)

            case exp.In():
                self._validate_in(expr, context)

            case exp.Exists():
                scope = self.scope.subquery_scopes[expr.this]
                validate_query(scope)

            case exp.Between():
                self._validate_between(expr, context)

            case exp.Like():
                self._validate_string(expr.this, context)
                self._validate_string(expr.expression, context)

            case _ if isinstance(
                expr,
                exp.Literal
                | exp.Boolean
                | exp.CurrentTime
                | exp.CurrentDate
                | exp.CurrentTimestamp,
            ):
                # Literal values do not require validation
                pass

            case _:
                raise NonScalarExpressionError(expr)

    def _validate_column(self, column: exp.Column, context: ValidationContext) -> None:
        if not self.scope.tables.can_resolve(column):
            raise ColumnNotFoundError.from_column(column)

        if (
            # Scenario: Grouped HAVING, SELECT, or ORDER BY
            (
                self.scope.is_grouped
                and (context.in_having or context.in_select or context.in_order_by)
            )
            # Condition: Column must be in the GROUP BY clause or appear in an aggregate function
            and not (column in self.scope.group_by or context.in_aggregate)
        ) or (
            # Scenario: Ungrouped HAVING
            (not self.scope.is_grouped and context.in_having)
            # Condition: Column must be in an aggregate function
            and not context.in_aggregate
        ):
            raise UngroupedColumnError(column, [column.name])

    def _validate_scalar_subquery(self, subquery: exp.Subquery) -> DataType:
        from .query import validate_query

        select = subquery.this

        # Validate the subquery
        scope = self.scope.subquery_scopes[select]
        if not isinstance(scope, SelectScope):
            raise NonScalarExpressionError(subquery)

        validate_query(scope)

        # Check if the subquery returns a scalar: a single column and a single row
        if len(scope.projections.expressions) != 1:
            raise NonScalarExpressionError(subquery)

        [expr] = scope.projections.expressions

        inner: Expression = expr.unalias()  # type: ignore[no-untyped-call]
        if not is_aggregate(inner) or scope.is_grouped:
            raise NonScalarExpressionError(subquery)

        return self._type_inferrer.infer(inner)

    def _validate_comparison(self, comp: Comparison, context: ValidationContext) -> None:
        # Validate and infer the type of the left side
        left = comp.left
        self.validate(left, context)
        lt = self._type_inferrer.infer(left)

        # Validate and infer the type of the right side
        right = comp.right
        match right:
            case exp.All() | exp.Any():
                query = right.this
                if isinstance(query, exp.Subquery):
                    # Unwrap the subquery
                    query = query.this
                rt = self._validate_quantified_predicate_query(query)
            case exp.Subquery():
                rt = self._validate_scalar_subquery(right)
            case _:
                self.validate(right, context)
                rt = self._type_inferrer.infer(right)

        assert_comparable(lt, rt, comp)

    def _validate_arithmetic_operation(
        self, op: ArithmeticOperation, context: ValidationContext
    ) -> None:
        self.validate(op.left, context)
        lt = self._type_inferrer.infer(op.left)

        self.validate(op.right, context)
        rt = self._type_inferrer.infer(op.right)

        if not (lt.is_numeric() and rt.is_numeric()):
            raise ArithmeticTypeMismatchError(op, lt, rt)

    def _validate_aggregate(self, aggr: AggregateFunction, context: ValidationContext) -> None:
        # Cannot be used in the WHERE clause
        if context.in_where:
            raise AggregateInWhereError(aggr)
        # Cannot be nested
        if context.in_aggregate:
            raise NestedAggregateError(aggr)

        arg: Expression = aggr.this
        context = context.enter_aggregate()
        match aggr:
            case exp.Count():
                if not arg.is_star:
                    self.validate(arg, context)

            case exp.Avg() | exp.Sum():
                self._validate_numeric(arg, context)

            case exp.Min() | exp.Max():
                self.validate(arg, context)

    def _validate_string_operation(self, op: StringOperation, context: ValidationContext) -> None:
        match op:
            case exp.Lower() | exp.Upper() | exp.Trim() | exp.Length():
                self._validate_string(op.this, context)

            case exp.Substring():
                self._validate_string(op.this, context)
                if start := op.args.get('start'):
                    self._validate_numeric(start, context)
                if length := op.args.get('length'):
                    self._validate_numeric(length, context)

            case exp.DPipe():
                self._validate_string(op.left, context)
                self._validate_string(op.right, context)

            case exp.StrPosition():
                self._validate_string(op.this, context)
                self._validate_string(op.args['substr'], context)

    def _validate_cast(self, cast: exp.Cast, context: ValidationContext) -> None:
        self.validate(cast.this, context)

        source_t = self._type_inferrer.infer(cast.this)
        target_t = convert_sqlglot_type(cast.args['to'])

        if not source_t.can_cast_to(target_t):
            raise InvalidCastError(cast, source_t, target_t)

    def _validate_boolean_expr(self, expr: BooleanExpression, context: ValidationContext) -> None:
        match expr:
            case exp.And() | exp.Or():
                self.validate_boolean(expr.left, context)
                self.validate_boolean(expr.right, context)

            case exp.Not():
                self.validate_boolean(expr.this, context)

    def _validate_in(self, pred: exp.In, context: ValidationContext) -> None:
        self.validate(pred.this, context)
        lt = self._type_inferrer.infer(pred.this)

        # Validate and infer the type of the right side
        if subquery := pred.args.get('query'):
            rt = self._validate_quantified_predicate_query(subquery.this)
            assert_comparable(lt, rt, pred)
        else:
            # If the IN clause is not a subquery, it must be a list of literals
            for val in pred.expressions:
                self.validate(val, context)
                rt = self._type_inferrer.infer(val)
                assert_comparable(lt, rt, pred)

    def _validate_quantified_predicate_query(self, query: SQLQuery) -> DataType:
        from .query import validate_query

        scope = self.scope.subquery_scopes[query]
        validate_query(scope)

        result = scope.projections
        if len(result.expressions) != 1:
            raise ColumnCountMismatchError(query, 1, len(result.expressions))
        [t] = result.types
        return t

    def _validate_between(self, pred: exp.Between, context: ValidationContext) -> None:
        expr = pred.this

        self.validate(expr, context)
        expr_t = self._type_inferrer.infer(expr)

        self.validate(pred.args['low'], context)
        low_t = self._type_inferrer.infer(pred.args['low'])

        self.validate(pred.args['high'], context)
        high_t = self._type_inferrer.infer(pred.args['high'])

        assert_comparable(expr_t, low_t, pred)
        assert_comparable(expr_t, high_t, pred)

    # ──────── Type Utilities ────────

    def validate_boolean(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self._validate_type(assert_boolean, expr, context)

    def _validate_numeric(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self._validate_type(assert_numeric, expr, context)

    def _validate_string(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self._validate_type(assert_string, expr, context)

    def _validate_type(
        self,
        assertion: Callable[[DataType, Expression], None],
        expr: Expression,
        context: ValidationContext | None = None,
    ) -> None:
        self.validate(expr, context)
        assertion(self._type_inferrer.infer(expr), expr)
