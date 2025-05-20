from collections.abc import Callable

from queries.services.types import SQLQuery
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import (
    Alias,
    All,
    And,
    Any,
    Avg,
    Between,
    Boolean,
    Cast,
    Coalesce,
    Column,
    Count,
    CurrentDate,
    CurrentTime,
    CurrentTimestamp,
    DPipe,
    Exists,
    Expression,
    In,
    Is,
    Length,
    Like,
    Literal,
    Lower,
    Max,
    Min,
    Not,
    Or,
    Paren,
    Star,
    StrPosition,
    Subquery,
    Substring,
    Sum,
    Trim,
    Upper,
)

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
        node: Expression,
        context: ValidationContext | None = None,
    ) -> None:
        from .query import QueryValidator

        if context is None:
            context = ValidationContext()
        match node:
            # Primary Expressions
            case Column():
                self._validate_column(node, context)

            case Subquery():
                self._validate_scalar_subquery(node)

            case Alias() | Paren() | Is() | Coalesce():
                self.validate(node.this, context)

            # Comparison
            case comp if isinstance(comp, Comparison):
                self._validate_comparison(comp, context)

            # Expressions
            case op if isinstance(op, ArithmeticOperation):
                self._validate_arithmetic_operation(node, context)

            case aggr if isinstance(aggr, AggregateFunction):
                self._validate_aggregate(aggr, context)

            case op if isinstance(op, StringOperation):
                self._validate_string_operation(node, context)

            case Cast():
                self._validate_cast(node, context)

            # Predicates
            case expr if isinstance(expr, BooleanExpression):
                self._validate_boolean_expr(node, context)

            case In():
                self._validate_in(node, context)

            case Exists():
                scope = self.scope.subquery_scopes[node.this]
                QueryValidator().validate(scope)

            case Between():
                self._validate_between(node, context)

            case Like():
                self._validate_string(node.this, context)
                self._validate_string(node.expression, context)

            case _ if isinstance(
                node, Literal | Boolean | CurrentTime | CurrentDate | CurrentTimestamp
            ):
                pass

            case _:
                raise NonScalarExpressionError(node)

    # ──────── Primary Expressions ────────
    def _validate_column(self, column: Column, context: ValidationContext) -> None:
        if self.scope.tables.resolve_column(column) is None:
            raise ColumnNotFoundError.from_column(column)

        if (
            # Scenario: Grouped HAVING, SELECT, or ORDER BY
            (
                self.scope.is_grouped
                and (context.in_having or context.in_select or context.in_order_by)
            )
            # Condition: Column must be in the GROUP BY clause or appear in an aggregate function
            and not (self.scope.group_by.contains(column) or context.in_aggregate)
        ) or (
            # Scenario: Ungrouped HAVING
            (not self.scope.is_grouped and context.in_having)
            # Condition: Column must be in an aggregate function
            and not context.in_aggregate
        ):
            raise UngroupedColumnError(column, [column.name])

    def _validate_scalar_subquery(self, subquery: Subquery) -> DataType:
        from .query import QueryValidator

        select = subquery.this

        scope = self.scope.subquery_scopes[select]
        QueryValidator().validate(scope)

        if len(scope.projections.expressions) != 1:
            raise NonScalarExpressionError(subquery)

        [(expr, t)] = scope.projections.expressions.items()

        inner: Expression = expr.unalias()  # type: ignore[no-untyped-call]
        if not is_aggregate(inner) or select.args.get('group'):
            raise NonScalarExpressionError(subquery)

        return t

    def _validate_comparison(self, comp: Comparison, context: ValidationContext) -> None:
        self.validate(comp.left, context)

        lt = self._type_inferrer.infer(comp.left)
        match comp.right:
            case All() | Any():
                query = comp.right.this
                if isinstance(query, Subquery):
                    # Unwrap the subquery
                    query = query.this
                rt = self._validate_quantified_predicate_query(query)
            case Subquery():
                rt = self._validate_scalar_subquery(comp.right)
            case _:
                self.validate(comp.right, context)
                rt = self._type_inferrer.infer(comp.right)
        assert_comparable(lt, rt, comp)

    def _validate_arithmetic_operation(
        self, op: ArithmeticOperation, context: ValidationContext
    ) -> None:
        self.validate(op.left, context)
        self.validate(op.right, context)

        lt = self._type_inferrer.infer(op.left)
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

        arg = aggr.this
        context = context.enter_aggregate()
        match aggr:
            case Count():
                if not isinstance(arg, Star):
                    self.validate(arg, context)

            case Avg() | Sum():
                self._validate_numeric(arg, context)

            case Min() | Max():
                self.validate(arg, context)

    def _validate_string_operation(self, op: StringOperation, context: ValidationContext) -> None:
        match op:
            case Lower() | Upper() | Trim() | Length():
                self._validate_string(op.this, context)

            case Substring():
                self._validate_string(op.this, context)
                if start := op.args.get('start'):
                    self._validate_numeric(start, context)
                if length := op.args.get('length'):
                    self._validate_numeric(length, context)

            case DPipe():
                self._validate_string(op.left, context)
                self._validate_string(op.right, context)

            case StrPosition():
                self._validate_string(op.this, context)
                self._validate_string(op.args['substr'], context)

    def _validate_cast(self, cast: Cast, context: ValidationContext) -> None:
        self.validate(cast.this, context)

        source_t = self._type_inferrer.infer(cast.this)
        target_t = convert_sqlglot_type(cast.args['to'])

        if not source_t.can_cast_to(target_t):
            raise InvalidCastError(cast, source_t, target_t)

    def _validate_boolean_expr(self, expr: BooleanExpression, context: ValidationContext) -> None:
        match expr:
            case And() | Or():
                self.validate_boolean(expr.left, context)
                self.validate_boolean(expr.right, context)

            case Not():
                self.validate_boolean(expr.this, context)

    def _validate_in(self, pred: In, context: ValidationContext) -> None:
        self.validate(pred.this, context)
        lt = self._type_inferrer.infer(pred.this)

        if subquery := pred.args.get('query'):
            rt = self._validate_quantified_predicate_query(subquery.this)
            assert_comparable(lt, rt, pred)
        else:
            # If the IN clause is not a subquery, it must be a list of literals
            for val in pred.expressions:
                rt = self._type_inferrer.infer(val)
                assert_comparable(lt, rt, pred)

    def _validate_quantified_predicate_query(self, query: SQLQuery) -> DataType:
        from .query import QueryValidator

        scope = self.scope.subquery_scopes[query]
        QueryValidator().validate(scope)

        if len(scope.projections.expressions) != 1:
            raise ColumnCountMismatchError(query, 1, len(scope.projections.expressions))
        [t] = scope.projections.types
        return t

    def _validate_between(self, pred: Between, context: ValidationContext) -> None:
        expr = pred.this
        self.validate(expr, context)

        expr_t = self._type_inferrer.infer(expr)
        low_t = self._type_inferrer.infer(pred.args['low'])
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
