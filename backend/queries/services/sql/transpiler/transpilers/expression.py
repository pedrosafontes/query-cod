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
from queries.services.sql.semantics.types import (
    BooleanExpression as SQLBooleanExpression,
)
from queries.services.sql.semantics.types import (
    Comparison as SQLComparison,
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


class ExpressionTranspiler:
    def transpile(
        self,
        expr: Expression,
    ) -> BooleanExpression:
        match expr:
            # case Boolean():
            #     return bool(expr.this)

            # case CurrentTime():
            #     return DataType.TIME

            # case CurrentDate():
            #     return DataType.DATE

            # case CurrentTimestamp():
            #     return DataType.TIMESTAMP

            # Primary Expressions
            case Column():
                # if isinstance(node.this, Star):
                #     return self._validate_star_expansion(node, node.table)
                # else:
                # return self._validate_column(node, context)
                return self.transpile_column(expr)

            # case Star():
            #     return self._validate_star_expansion(node)

            # case Alias():
            #     return self.validate(node.this, context)

            # case Subquery():
            #     return self._validate_scalar_subquery(node)

            case Paren():
                return self.transpile(expr.this)

            # Comparison
            case comp if isinstance(comp, SQLComparison):
                return self._transpile_comparison(comp)

            # Expressions
            # case op if isinstance(op, ArithmeticOperation):
            #     return self._validate_arithmetic_operation(node, context)

            # case aggr if isinstance(aggr, AggregateFunction):
            #     return self._validate_aggregate(aggr, context)

            # case op if isinstance(op, StringOperation):
            #     return self._validate_string_operation(node, context)

            # case Cast():
            #     return self._validate_cast(node, context)

            # Predicates
            case expr if isinstance(expr, SQLBooleanExpression):
                return self._transpile_boolean_expr(expr)

            # case Exists():
            #     self.query_validator.validate(node.this, self.scope)
            #     return DataType.BOOLEAN

            # case Between():
            #     return self._validate_between(node, context)

            # case Like():
            #     self._validate_string(node.this, context)
            #     self._validate_string(node.expression, context)
            #     return DataType.BOOLEAN

            # case Is():
            #     self.validate_basic(node.this, context)
            #     return DataType.BOOLEAN

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

    # # ──────── Expressions ────────
    # def _validate_arithmetic_operation(
    #     self, op: ArithmeticOperation, context: ValidationContext
    # ) -> DataType:
    #     lt = self.validate_basic(op.left, context)
    #     rt = self.validate_basic(op.right, context)

    #     if lt.is_numeric() and rt.is_numeric():
    #         return DataType.dominant([lt, rt])

    #     raise ArithmeticTypeMismatchError(op, lt, rt)

    # def _validate_aggregate(self, aggr: AggregateFunction, context: ValidationContext) -> DataType:
    #     # Cannot be used in the WHERE clause
    #     if context.in_where:
    #         raise AggregateInWhereError(aggr)
    #     # Cannot be nested
    #     if context.in_aggregate:
    #         raise NestedAggregateError(aggr)

    #     arg = aggr.this
    #     context = context.enter_aggregate()
    #     match aggr:
    #         case Count():
    #             if not isinstance(arg, Star):
    #                 self.validate(arg, context)
    #             return DataType.INTEGER

    #         case Avg() | Sum():
    #             return self._validate_numeric(arg, context)

    #         case Min() | Max():
    #             return self.validate_basic(arg, context)

    # def _validate_string_operation(
    #     self, op: StringOperation, context: ValidationContext
    # ) -> DataType:
    #     match op:
    #         case Lower() | Upper() | Trim():
    #             return self._validate_string(op.this, context)

    #         case Length():
    #             self._validate_string(op.this, context)
    #             return DataType.INTEGER

    #         case Substring():
    #             self._validate_string(op.this, context)
    #             if start := op.args.get('start'):
    #                 self._validate_numeric(start, context)
    #             if length := op.args.get('length'):
    #                 self._validate_numeric(length, context)
    #             return DataType.VARCHAR

    #         case DPipe():
    #             self._validate_string(op.left, context)
    #             self._validate_string(op.right, context)
    #             return DataType.VARCHAR

    #         case StrPosition():
    #             self._validate_string(op.this, context)
    #             self._validate_string(op.args['substr'], context)
    #             return DataType.INTEGER

    # def _validate_cast(self, cast: Cast, context: ValidationContext) -> DataType:
    #     source_t = self.validate_basic(cast.this, context)
    #     target_t = convert_sqlglot_type(cast.args['to'])

    #     if not source_t.can_cast_to(target_t):
    #         raise InvalidCastError(cast, source_t, target_t)

    #     return target_t

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

    # def _validate_in(self, pred: In, context: ValidationContext) -> DataType:
    #     lt = self.validate_basic(pred.this, context)
    #     if subquery := pred.args.get('query'):
    #         rt = self._validate_quantified_predicate_query(subquery.this)
    #         assert_comparable(lt, rt, pred)
    #     else:
    #         # If the IN clause is not a subquery, it must be a list of literals
    #         for val in pred.expressions:
    #             rt = self.validate_basic(val, context)
    #             assert_comparable(lt, rt, pred)
    #     return DataType.BOOLEAN

    # def _validate_quantified_predicate_query(self, query: Expression) -> DataType:
    #     schema = self.query_validator.validate(query, self.scope).schema
    #     try:
    #         [(_, columns)] = schema.items()  # Single table
    #         [(_, rt)] = columns.items()  # Single column
    #     except ValueError:  # Unpack error
    #         raise ColumnCountMismatchError(query, 1, len(columns)) from None
    #     return rt

    # def _validate_between(self, pred: Between, context: ValidationContext) -> DataType:
    #     t = self.validate_basic(pred.this, context)
    #     low_t = self.validate_basic(pred.args['low'], context)
    #     high_t = self.validate_basic(pred.args['high'], context)

    #     assert_comparable(t, low_t, pred)
    #     assert_comparable(t, high_t, pred)

    #     return DataType.BOOLEAN

    # # ──────── Type Utilities ────────

    # def _validate_boolean(
    #     self, expr: Expression, context: ValidationContext | None = None
    # ) -> DataType:
    #     t = self.validate_basic(expr, context)
    #     assert_boolean(t, expr)
    #     return t

    # def _validate_numeric(
    #     self, expr: Expression, context: ValidationContext | None = None
    # ) -> DataType:
    #     t = self.validate_basic(expr, context)
    #     assert_numeric(t, expr)
    #     return t

    # def _validate_string(
    #     self, expr: Expression, context: ValidationContext | None = None
    # ) -> DataType:
    #     t = self.validate_basic(expr, context)
    #     assert_string(t, expr)
    #     return t
