from databases.types import Schema
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
    NonScalarExpressionError,
    UngroupedColumnError,
)
from ..scope import Scope
from ..type_utils import (
    assert_boolean,
    assert_comparable,
    assert_numeric,
    assert_scalar_subquery,
    assert_string,
    convert_sqlglot_type,
    infer_literal_type,
)
from ..types import (
    AggregateFunction,
    ArithmeticOperation,
    BooleanExpression,
    Comparison,
    StringOperation,
)


class ExpressionValidator:
    def __init__(self, schema: Schema, scope: Scope) -> None:
        from .query import QueryValidator

        self.scope = scope
        self.query_validator = QueryValidator(schema)

    def validate_basic(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> DataType:
        t = self.validate(node, context)

        if isinstance(t, DataType):
            return t
        else:
            raise NonScalarExpressionError(node)

    def validate(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> DataType | RelationalSchema:
        if context is None:
            context = ValidationContext()

        match node:
            # Literals
            case Literal():
                return infer_literal_type(node)

            case Boolean():
                return DataType.BOOLEAN

            case CurrentTime():
                return DataType.TIME

            case CurrentDate():
                return DataType.DATE

            case CurrentTimestamp():
                return DataType.TIMESTAMP

            # Primary Expressions
            case Column():
                if isinstance(node.this, Star):
                    return self._validate_star_expansion(node, node.table)
                else:
                    return self._validate_column(node, context)

            case Star():
                return self._validate_star_expansion(node)

            case Alias():
                return self.validate(node.this, context)

            case Subquery():
                return self._validate_scalar_subquery(node)

            case Paren():
                return self.validate(node.this, context)

            # Comparison
            case comp if isinstance(comp, Comparison):
                return self._validate_comparison(comp, context)

            # Expressions
            case op if isinstance(op, ArithmeticOperation):
                return self._validate_arithmetic_operation(node, context)

            case aggr if isinstance(aggr, AggregateFunction):
                return self._validate_aggregate(aggr, context)

            case op if isinstance(op, StringOperation):
                return self._validate_string_operation(node, context)

            case Cast():
                return self._validate_cast(node, context)

            # Predicates
            case expr if isinstance(expr, BooleanExpression):
                return self._validate_boolean_expr(node, context)

            case In():
                return self._validate_in(node, context)

            case Any() | All():
                query_expr = node.this
                if isinstance(query_expr, Subquery):
                    # Unwrap the subquery
                    query_expr = query_expr.this
                return self._validate_quantified_predicate_query(query_expr)

            case Exists():
                self.query_validator.validate(node.this, self.scope)
                return DataType.BOOLEAN

            case Between():
                return self._validate_between(node, context)

            case Like():
                self._validate_string(node.this, context)
                self._validate_string(node.expression, context)
                return DataType.BOOLEAN

            case Is():
                self.validate_basic(node.this, context)
                return DataType.BOOLEAN

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    # ──────── Primary Expressions ────────
    def _validate_column(self, column: Column, context: ValidationContext) -> DataType:
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
        return t

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
        try:
            assert_scalar_subquery(subquery)
            [(_, columns)] = sub_schema.items()  # Single table
            [(_, t)] = columns.items()  # Single column
        except ValueError:  # Unpack error
            # Subquery must return a single table with a single column
            raise NonScalarExpressionError(subquery) from None
        return t

    # ──────── Comparison ────────
    def _validate_comparison(self, comp: Comparison, context: ValidationContext) -> DataType:
        lt = self.validate_basic(comp.left, context)
        rt = self.validate_basic(comp.right, context)
        assert_comparable(lt, rt, comp)
        return DataType.BOOLEAN

    # ──────── Expressions ────────
    def _validate_arithmetic_operation(
        self, op: ArithmeticOperation, context: ValidationContext
    ) -> DataType:
        lt = self.validate_basic(op.left, context)
        rt = self.validate_basic(op.right, context)

        if lt.is_numeric() and rt.is_numeric():
            return DataType.dominant([lt, rt])

        raise ArithmeticTypeMismatchError(op, lt, rt)

    def _validate_aggregate(self, aggr: AggregateFunction, context: ValidationContext) -> DataType:
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
                return DataType.INTEGER

            case Avg() | Sum():
                return self._validate_numeric(arg, context)

            case Min() | Max():
                return self.validate_basic(arg, context)

    def _validate_string_operation(
        self, op: StringOperation, context: ValidationContext
    ) -> DataType:
        match op:
            case Lower() | Upper() | Trim():
                return self._validate_string(op.this, context)

            case Length():
                self._validate_string(op.this, context)
                return DataType.INTEGER

            case Substring():
                self._validate_string(op.this, context)
                if start := op.args.get('start'):
                    self._validate_numeric(start, context)
                if length := op.args.get('length'):
                    self._validate_numeric(length, context)
                return DataType.VARCHAR

            case DPipe():
                self._validate_string(op.left, context)
                self._validate_string(op.right, context)
                return DataType.VARCHAR

            case StrPosition():
                self._validate_string(op.this, context)
                self._validate_string(op.args['substr'], context)
                return DataType.INTEGER

    def _validate_cast(self, cast: Cast, context: ValidationContext) -> DataType:
        source_t = self.validate_basic(cast.this, context)
        target_t = convert_sqlglot_type(cast.args['to'])

        if not source_t.can_cast_to(target_t):
            raise InvalidCastError(cast, source_t, target_t)

        return target_t

    # ──────── Predicate Expressions ────────
    def _validate_boolean_expr(
        self, expr: BooleanExpression, context: ValidationContext
    ) -> DataType:
        match expr:
            case And() | Or():
                self._validate_boolean(expr.left, context)
                self._validate_boolean(expr.right, context)

            case Not():
                self._validate_boolean(expr.this, context)
        return DataType.BOOLEAN

    def _validate_in(self, pred: In, context: ValidationContext) -> DataType:
        lt = self.validate_basic(pred.this, context)
        if subquery := pred.args.get('query'):
            rt = self._validate_quantified_predicate_query(subquery.this)
            assert_comparable(lt, rt, pred)
        else:
            # If the IN clause is not a subquery, it must be a list of literals
            for val in pred.expressions:
                rt = self.validate_basic(val, context)
                assert_comparable(lt, rt, pred)
        return DataType.BOOLEAN

    def _validate_quantified_predicate_query(self, query: Expression) -> DataType:
        schema = self.query_validator.validate(query, self.scope).schema
        try:
            [(_, columns)] = schema.items()  # Single table
            [(_, rt)] = columns.items()  # Single column
        except ValueError:  # Unpack error
            raise ColumnCountMismatchError(query, 1, len(columns)) from None
        return rt

    def _validate_between(self, pred: Between, context: ValidationContext) -> DataType:
        t = self.validate_basic(pred.this, context)
        low_t = self.validate_basic(pred.args['low'], context)
        high_t = self.validate_basic(pred.args['high'], context)

        assert_comparable(t, low_t, pred)
        assert_comparable(t, high_t, pred)

        return DataType.BOOLEAN

    # ──────── Type Utilities ────────

    def _validate_boolean(
        self, expr: Expression, context: ValidationContext | None = None
    ) -> DataType:
        t = self.validate_basic(expr, context)
        assert_boolean(t, expr)
        return t

    def _validate_numeric(
        self, expr: Expression, context: ValidationContext | None = None
    ) -> DataType:
        t = self.validate_basic(expr, context)
        assert_numeric(t, expr)
        return t

    def _validate_string(
        self, expr: Expression, context: ValidationContext | None = None
    ) -> DataType:
        t = self.validate_basic(expr, context)
        assert_string(t, expr)
        return t
