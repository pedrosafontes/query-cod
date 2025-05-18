from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType
from sqlglot import Expression
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

from ..context import ValidationContext
from ..errors import (
    AggregateInWhereError,
    ArithmeticTypeMismatchError,
    ColumnCountMismatchError,
    ColumnNotFoundError,
    InvalidCastError,
    NestedAggregateError,
    UngroupedColumnError,
)
from ..errors.data_type import NonScalarExpressionError
from ..inferrer import infer_type
from ..scope import Scope
from ..types import (
    AggregateFunction,
    ArithmeticOperation,
    BooleanExpression,
    Comparison,
    StringOperation,
)
from ..utils import (
    assert_boolean,
    assert_comparable,
    assert_numeric,
    assert_scalar_subquery,
    assert_string,
    convert_sqlglot_type,
)


class ExpressionValidator:
    def __init__(self, schema: RelationalSchema, scope: Scope) -> None:
        from .query import QueryValidator

        self.scope = scope
        self.query_validator = QueryValidator(schema)

    def validate(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> RelationalSchema | None:
        match node:
            case Column(this=Star()):
                return self._validate_star_expansion(node, node.table)
            case Star():
                return self._validate_star_expansion(node)
            case Alias() | Paren():
                return self.validate(node.this, context)
            case _:
                self.validate_basic(node, context)
                return None

    def validate_basic(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> None:
        if context is None:
            context = ValidationContext()

        match node:
            # Primary Expressions
            case Column():
                self._validate_column(node, context)

            case Subquery():
                self._validate_scalar_subquery(node)

            case Alias() | Paren() | Is() | Coalesce():
                self.validate_basic(node.this, context)

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
                self.query_validator.validate(node.this, self.scope)

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
        t = self.scope.tables.resolve_column(column)

        if t is None:
            raise ColumnNotFoundError.from_column(column)

        if (
            # Scenario: Grouped HAVING, SELECT, or ORDER BY
            (self.scope.is_grouped and not context.in_group_by)
            # Condition: Column must be in the GROUP BY clause or appear in an aggregate function
            and not (self.scope.group_by.contains(column) or context.in_aggregate)
        ) or (
            # Scenario: Ungrouped HAVING
            (not self.scope.is_grouped and context.in_having)
            # Condition: Column must be in an aggregate function
            and not context.in_aggregate
        ):
            raise UngroupedColumnError(column, [column.name])

    def _validate_star_expansion(
        self, source: Expression, table: str | None = None
    ) -> RelationalSchema:
        schema = (
            self.scope.tables.get_table_schema(table, source)
            if table
            else self.scope.tables.get_schema()
        )

        if self.scope.is_grouped:
            missing: list[str] = []
            for table, table_schema in schema.items():
                for col, _ in table_schema.items():
                    col_expr = Column(this=col, table=table)
                    if not self.scope.group_by.contains(col_expr):
                        missing.append(col)

            if missing:
                raise UngroupedColumnError(source, missing)

        return schema

    def _validate_scalar_subquery(self, subquery: Subquery) -> DataType:
        sub_schema = self.query_validator.validate(subquery.this, self.scope).schema
        assert_scalar_subquery(subquery)
        [(_, columns)] = sub_schema.items()
        [(_, t)] = columns.items()
        return t

    # ──────── Comparison ────────
    def _validate_comparison(self, comp: Comparison, context: ValidationContext) -> None:
        self.validate_basic(comp.left, context)

        lt = infer_type(comp.left, self.scope)
        match comp.right:
            case All() | Any():
                query_expr = comp.right.this
                if isinstance(query_expr, Subquery):
                    # Unwrap the subquery
                    query_expr = query_expr.this
                rt = self._validate_quantified_predicate_query(query_expr)
            case Subquery():
                rt = self._validate_scalar_subquery(comp.right)
            case _:
                self.validate_basic(comp.right, context)
                rt = infer_type(comp.right, self.scope)
        assert_comparable(lt, rt, comp)

    # ──────── Expressions ────────
    def _validate_arithmetic_operation(
        self, op: ArithmeticOperation, context: ValidationContext
    ) -> None:
        self.validate_basic(op.left, context)
        self.validate_basic(op.right, context)

        print(op.left.to_s())
        print(op.right.to_s())
        lt = infer_type(op.left, self.scope)
        rt = infer_type(op.right, self.scope)

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
                self.validate_basic(arg, context)

    def _validate_string_operation(self, op: StringOperation, context: ValidationContext) -> None:
        match op:
            case Lower() | Upper() | Trim():
                self._validate_string(op.this, context)

            case Length():
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
        self.validate_basic(cast.this, context)

        source_t = infer_type(cast.this, self.scope)
        target_t = convert_sqlglot_type(cast.args['to'])

        if not source_t.can_cast_to(target_t):
            raise InvalidCastError(cast, source_t, target_t)

    # ──────── Predicate Expressions ────────
    def _validate_boolean_expr(self, expr: BooleanExpression, context: ValidationContext) -> None:
        match expr:
            case And() | Or():
                self._validate_boolean(expr.left, context)
                self._validate_boolean(expr.right, context)

            case Not():
                self._validate_boolean(expr.this, context)

    def _validate_in(self, pred: In, context: ValidationContext) -> None:
        self.validate_basic(pred.this, context)
        lt = infer_type(pred.this, self.scope)
        if subquery := pred.args.get('query'):
            rt = self._validate_quantified_predicate_query(subquery.this)
            assert_comparable(lt, rt, pred)
        else:
            # If the IN clause is not a subquery, it must be a list of literals
            for val in pred.expressions:
                self.validate_basic(val, context)
                rt = infer_type(val, self.scope)
                assert_comparable(lt, rt, pred)

    def _validate_quantified_predicate_query(self, query: Expression) -> DataType:
        schema = self.query_validator.validate(query, self.scope).schema
        try:
            [(_, columns)] = schema.items()  # Single table
            [(_, rt)] = columns.items()  # Single column
        except ValueError:  # Unpack error
            raise ColumnCountMismatchError(query, 1, len(columns)) from None
        return rt

    def _validate_between(self, pred: Between, context: ValidationContext) -> None:
        self.validate_basic(pred.this, context)
        self.validate_basic(pred.args['low'], context)
        self.validate_basic(pred.args['high'], context)

        t = infer_type(pred.this, self.scope)
        low_t = infer_type(pred.args['low'], self.scope)
        high_t = infer_type(pred.args['high'], self.scope)

        assert_comparable(t, low_t, pred)
        assert_comparable(t, high_t, pred)

    # ──────── Type Utilities ────────

    def _validate_boolean(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self.validate_basic(expr, context)
        t = infer_type(expr, self.scope)
        assert_boolean(t, expr)

    def _validate_numeric(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self.validate_basic(expr, context)
        t = infer_type(expr, self.scope)
        assert_numeric(t, expr)

    def _validate_string(self, expr: Expression, context: ValidationContext | None = None) -> None:
        self.validate_basic(expr, context)
        t = infer_type(expr, self.scope)
        assert_string(t, expr)
