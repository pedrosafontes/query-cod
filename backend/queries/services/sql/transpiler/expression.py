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

from ..types import (
    BooleanExpression as SQLBooleanExpression,
)
from ..types import (
    Comparison as SQLComparison,
)


class ExpressionTranspiler:
    @staticmethod
    def transpile(
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
                #     return ExpressionTranspiler._validate_star_expansion(node, node.table)
                # else:
                # return ExpressionTranspiler._validate_column(node, context)
                return ExpressionTranspiler.transpile_column(expr)

            # case Star():
            #     return ExpressionTranspiler._validate_star_expansion(node)

            # case Alias():
            #     return ExpressionTranspiler.validate(node.this, context)

            # case Subquery():
            #     return ExpressionTranspiler._validate_scalar_subquery(node)

            case Paren():
                return ExpressionTranspiler.transpile(expr.this)

            # Comparison
            case comp if isinstance(comp, SQLComparison):
                return ExpressionTranspiler._transpile_comparison(comp)

            # Expressions
            # case op if isinstance(op, ArithmeticOperation):
            #     return ExpressionTranspiler._validate_arithmetic_operation(node, context)

            # case aggr if isinstance(aggr, AggregateFunction):
            #     return ExpressionTranspiler._validate_aggregate(aggr, context)

            # case op if isinstance(op, StringOperation):
            #     return ExpressionTranspiler._validate_string_operation(node, context)

            # case Cast():
            #     return ExpressionTranspiler._validate_cast(node, context)

            # Predicates
            case expr if isinstance(expr, SQLBooleanExpression):
                return ExpressionTranspiler._transpile_boolean_expr(expr)

            # case Exists():
            #     ExpressionTranspiler.query_validator.validate(node.this, ExpressionTranspiler.scope)
            #     return DataType.BOOLEAN

            # case Between():
            #     return ExpressionTranspiler._validate_between(node, context)

            # case Like():
            #     ExpressionTranspiler._validate_string(node.this, context)
            #     ExpressionTranspiler._validate_string(node.expression, context)
            #     return DataType.BOOLEAN

            # case Is():
            #     ExpressionTranspiler.validate_basic(node.this, context)
            #     return DataType.BOOLEAN

            case _:
                raise NotImplementedError(f'Expression {type(expr)} not supported')

    @staticmethod
    def transpile_column(
        expr: Column,
    ) -> Attribute:
        return Attribute(name=str(expr.this), relation=expr.table or None)

    @staticmethod
    def _transpile_value(
        value: Expression,
    ) -> ComparisonValue:
        match value:
            case Column():
                return ExpressionTranspiler.transpile_column(value)
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

    @staticmethod
    def _transpile_comparison(comp: SQLComparison) -> Comparison:
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
            left=ExpressionTranspiler._transpile_value(comp.left),
            right=ExpressionTranspiler._transpile_value(comp.right),
        )

    # # ──────── Expressions ────────
    # def _validate_arithmetic_operation(
    #     op: ArithmeticOperation, context: ValidationContext
    # ) -> DataType:
    #     lt = ExpressionTranspiler.validate_basic(op.left, context)
    #     rt = ExpressionTranspiler.validate_basic(op.right, context)

    #     if lt.is_numeric() and rt.is_numeric():
    #         return DataType.dominant([lt, rt])

    #     raise ArithmeticTypeMismatchError(op, lt, rt)

    # def _validate_aggregate(aggr: AggregateFunction, context: ValidationContext) -> DataType:
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
    #                 ExpressionTranspiler.validate(arg, context)
    #             return DataType.INTEGER

    #         case Avg() | Sum():
    #             return ExpressionTranspiler._validate_numeric(arg, context)

    #         case Min() | Max():
    #             return ExpressionTranspiler.validate_basic(arg, context)

    # def _validate_string_operation(
    #     op: StringOperation, context: ValidationContext
    # ) -> DataType:
    #     match op:
    #         case Lower() | Upper() | Trim():
    #             return ExpressionTranspiler._validate_string(op.this, context)

    #         case Length():
    #             ExpressionTranspiler._validate_string(op.this, context)
    #             return DataType.INTEGER

    #         case Substring():
    #             ExpressionTranspiler._validate_string(op.this, context)
    #             if start := op.args.get('start'):
    #                 ExpressionTranspiler._validate_numeric(start, context)
    #             if length := op.args.get('length'):
    #                 ExpressionTranspiler._validate_numeric(length, context)
    #             return DataType.VARCHAR

    #         case DPipe():
    #             ExpressionTranspiler._validate_string(op.left, context)
    #             ExpressionTranspiler._validate_string(op.right, context)
    #             return DataType.VARCHAR

    #         case StrPosition():
    #             ExpressionTranspiler._validate_string(op.this, context)
    #             ExpressionTranspiler._validate_string(op.args['substr'], context)
    #             return DataType.INTEGER

    # def _validate_cast(cast: Cast, context: ValidationContext) -> DataType:
    #     source_t = ExpressionTranspiler.validate_basic(cast.this, context)
    #     target_t = convert_sqlglot_type(cast.args['to'])

    #     if not source_t.can_cast_to(target_t):
    #         raise InvalidCastError(cast, source_t, target_t)

    #     return target_t

    # # ──────── Predicate Expressions ────────
    @staticmethod
    def _transpile_boolean_expr(
        expr: SQLBooleanExpression,
    ) -> BooleanExpression:
        match expr:
            case And():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.AND,
                    left=ExpressionTranspiler.transpile(expr.left),
                    right=ExpressionTranspiler.transpile(expr.right),
                )

            case Or():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.OR,
                    left=ExpressionTranspiler.transpile(expr.left),
                    right=ExpressionTranspiler.transpile(expr.right),
                )

            case Not():
                return NotExpression(
                    expression=ExpressionTranspiler.transpile(expr.this),
                )

    # def _validate_in(pred: In, context: ValidationContext) -> DataType:
    #     lt = ExpressionTranspiler.validate_basic(pred.this, context)
    #     if subquery := pred.args.get('query'):
    #         rt = ExpressionTranspiler._validate_quantified_predicate_query(subquery.this)
    #         assert_comparable(lt, rt, pred)
    #     else:
    #         # If the IN clause is not a subquery, it must be a list of literals
    #         for val in pred.expressions:
    #             rt = ExpressionTranspiler.validate_basic(val, context)
    #             assert_comparable(lt, rt, pred)
    #     return DataType.BOOLEAN

    # def _validate_quantified_predicate_query(query: Expression) -> DataType:
    #     schema = ExpressionTranspiler.query_validator.validate(query, ExpressionTranspiler.scope).schema
    #     try:
    #         [(_, columns)] = schema.items()  # Single table
    #         [(_, rt)] = columns.items()  # Single column
    #     except ValueError:  # Unpack error
    #         raise ColumnCountMismatchError(query, 1, len(columns)) from None
    #     return rt

    # def _validate_between(pred: Between, context: ValidationContext) -> DataType:
    #     t = ExpressionTranspiler.validate_basic(pred.this, context)
    #     low_t = ExpressionTranspiler.validate_basic(pred.args['low'], context)
    #     high_t = ExpressionTranspiler.validate_basic(pred.args['high'], context)

    #     assert_comparable(t, low_t, pred)
    #     assert_comparable(t, high_t, pred)

    #     return DataType.BOOLEAN
