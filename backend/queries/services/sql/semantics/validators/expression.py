from databases.types import Schema
from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
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
)

from ..context import ValidationContext
from ..errors import (
    AggregateInWhereError,
    ArithmeticTypeMismatchError,
    ColumnCountMismatchError,
    InvalidCastError,
    NestedAggregateError,
    NonGroupedColumnError,
    ScalarExpressionExpectedError,
    ScalarSubqueryError,
    UndefinedColumnError,
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
from ..types import ArithmeticOperation, StringOperation


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
            raise ScalarExpressionExpectedError(node)

    def validate(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> DataType | RelationalSchema:
        if context is None:
            context = ValidationContext()
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                if isinstance(node.this, Star):
                    return self._validate_star_expansion(node, node.table)
                else:
                    return self._validate_column(node, context)

            case Alias():
                return self.validate(node.this, context)

            case And() | Or():
                self._validate_boolean(node.left, context)
                self._validate_boolean(node.right, context)
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                lt = self.validate_basic(node.left, context)
                rt = self.validate_basic(node.right, context)
                assert_comparable(lt, rt, node)
                return DataType.BOOLEAN

            case op if isinstance(op, ArithmeticOperation):
                return self._validate_arithmetic_operation(node, context)

            case Not():
                self._validate_boolean(node.this, context)
                return DataType.BOOLEAN

            case Count():
                self._validate_aggregate_context(node, context)
                arg = node.this
                if not isinstance(arg, Star):
                    self.validate(arg, context.enter_aggregate())
                return DataType.INTEGER

            case Avg() | Sum():
                self._validate_aggregate_context(node, context)
                return self._validate_numeric(node.this, context.enter_aggregate())

            case Min() | Max():
                self._validate_aggregate_context(node, context)
                return self.validate_basic(node.this, context.enter_aggregate())

            case Star():
                return self._validate_star_expansion(node)

            case Subquery():
                sub_schema = self.query_validator.validate(node.this, self.scope).schema
                try:
                    assert_scalar_subquery(node)
                    [(_, columns)] = sub_schema.items()  # Single table
                    [(_, t)] = columns.items()  # Single column
                except ValueError:  # Unpack error
                    # Subquery must return a single table with a single column
                    raise ScalarSubqueryError(node) from None
                return t

            case In():
                lt = self.validate_basic(node.this, context)
                if subquery := node.args.get('query'):
                    rt = self._validate_quantified_predicate_query(subquery.this)
                    assert_comparable(lt, rt, node)
                else:
                    # If the IN clause is not a subquery, it must be a list of literals
                    for val in node.expressions:
                        rt = self.validate_basic(val, context)
                        assert_comparable(lt, rt, node)
                return DataType.BOOLEAN

            case Any() | All():
                query_expr = node.this
                if isinstance(query_expr, Subquery):
                    # Unwrap the subquery
                    query_expr = query_expr.this
                return self._validate_quantified_predicate_query(query_expr)

            case Exists():
                self.query_validator.validate(node.this, self.scope)
                return DataType.BOOLEAN

            case Paren():
                return self.validate(node.this, context)

            case Boolean():
                return DataType.BOOLEAN

            case Length():
                self._validate_string(node.this, context)
                return DataType.INTEGER

            case op if isinstance(op, StringOperation):
                return self._validate_string(node.this, context)

            case Substring():
                self._validate_string(node.this, context)
                if start := node.args.get('start'):
                    self._validate_numeric(start, context)
                if length := node.args.get('length'):
                    self._validate_numeric(length, context)
                return DataType.VARCHAR

            case DPipe():
                self._validate_string(node.left, context)
                self._validate_string(node.right, context)
                return DataType.VARCHAR

            case StrPosition():
                self._validate_string(node.this, context)
                self._validate_string(node.args['substr'], context)
                return DataType.INTEGER

            case Between():
                t = self.validate_basic(node.this, context)
                low_t = self.validate_basic(node.args['low'], context)
                high_t = self.validate_basic(node.args['high'], context)

                assert_comparable(t, low_t, node)
                assert_comparable(t, high_t, node)

                return DataType.BOOLEAN

            case Like():
                self._validate_string(node.this, context)
                self._validate_string(node.expression, context)
                return DataType.BOOLEAN

            case Is():
                self.validate_basic(node.this, context)
                return DataType.BOOLEAN

            case Cast():
                source_t = self.validate_basic(node.this, context)
                target_t = convert_sqlglot_type(node.args['to'])

                if not source_t.can_cast_to(target_t):
                    raise InvalidCastError(node, source_t, target_t)

                return target_t

            case CurrentTime():
                return DataType.TIME

            case CurrentDate():
                return DataType.DATE

            case CurrentTimestamp():
                return DataType.TIMESTAMP

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    def _validate_column(self, column: Column, context: ValidationContext) -> DataType:
        t = self.scope.tables.resolve_column(column)

        if t is None:
            raise UndefinedColumnError.from_column(column)

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
            raise NonGroupedColumnError(column, [column.name])
        return t

    def _validate_aggregate_context(self, source: Expression, context: ValidationContext) -> None:
        # Cannot be used in the WHERE clause
        if context.in_where:
            raise AggregateInWhereError(source)
        # Cannot be nested
        if context.in_aggregate:
            raise NestedAggregateError(source)

    def _validate_quantified_predicate_query(self, query: Expression) -> DataType:
        schema = self.query_validator.validate(query, self.scope).schema
        try:
            [(_, columns)] = schema.items()  # Single table
            [(_, rt)] = columns.items()  # Single column
        except ValueError:  # Unpack error
            raise ColumnCountMismatchError(query, 1, len(columns)) from None
        return rt

    # ──────── Star Expansion Validations ────────

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
                raise NonGroupedColumnError(source, missing)

        return schema

    def _validate_arithmetic_operation(
        self, op: ArithmeticOperation, context: ValidationContext
    ) -> DataType:
        lt = self.validate_basic(op.left, context)
        rt = self.validate_basic(op.right, context)

        if lt.is_numeric() and rt.is_numeric():
            return DataType.dominant([lt, rt])

        raise ArithmeticTypeMismatchError(op, lt, rt)

    # ──────── Type Utilities ────────

    def _validate_boolean(self, expr: Expression, context: ValidationContext | None = None) -> None:
        assert_boolean(self.validate_basic(expr, context), expr)

    def _validate_numeric(self, expr: Expression, context: ValidationContext) -> DataType:
        t = self.validate_basic(expr, context)
        assert_numeric(t, expr)
        return t

    def _validate_string(self, expr: Expression, context: ValidationContext) -> DataType:
        t = self.validate_basic(expr, context)
        assert_string(t, expr)
        return t
