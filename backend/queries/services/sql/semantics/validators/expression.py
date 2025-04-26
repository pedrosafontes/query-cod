from typing import cast

from databases.types import Schema
from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    Add,
    Alias,
    All,
    And,
    Any,
    Avg,
    Boolean,
    Column,
    Count,
    Div,
    Exists,
    In,
    Literal,
    Max,
    Min,
    Mul,
    Not,
    Or,
    Paren,
    Star,
    Sub,
    Subquery,
    Sum,
)

from ..context import ValidationContext
from ..errors import (
    AggregateInWhereError,
    ColumnCountMismatchError,
    NestedAggregateError,
    NonGroupedColumnError,
    ScalarSubqueryError,
    UndefinedColumnError,
)
from ..scope import Scope
from ..type_utils import (
    assert_boolean,
    assert_comparable,
    assert_numeric,
    assert_orderable,
    assert_scalar_subquery,
    infer_literal_type,
)
from ..types import ResultSchema


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
        return cast(DataType, self.validate(node, context))

    def validate(
        self,
        node: Expression,
        context: ValidationContext | None = None,
    ) -> DataType | ResultSchema:
        if context is None:
            context = ValidationContext()
        match node:
            case Literal():
                return infer_literal_type(node)

            case Column():
                if isinstance(node.this, Star):
                    return self._validate_star_expansion(node.table)
                else:
                    t = self._validate_column(node, context)

                    if (
                        # Scenario: Grouped HAVING, SELECT, or ORDER BY
                        (self.scope.is_grouped and not context.in_group_by)
                        # Condition: Column must be in the GROUP BY clause or appear in an aggregate function
                        and not (self.scope.group_by.contains(node) or context.in_aggregate)
                    ) or (
                        # Scenario: Grouped HAVING
                        (not self.scope.is_grouped and context.in_having)
                        # Condition: Column must be in an aggregate function
                        and not context.in_aggregate
                    ):
                        raise NonGroupedColumnError([node.name])
                    return t

            case Alias():
                return self.validate(node.this, context)

            case And() | Or():
                lt = self.validate_basic(node.left, context)
                rt = self.validate_basic(node.right, context)
                assert_boolean(lt)
                assert_boolean(rt)
                return DataType.BOOLEAN

            case EQ() | NEQ() | LT() | LTE() | GT() | GTE():
                lt = self.validate_basic(node.left, context)
                rt = self.validate_basic(node.right, context)
                assert_comparable(lt, rt)
                return DataType.BOOLEAN

            case Add() | Sub() | Mul() | Div():
                lt = self.validate_basic(node.left, context)
                rt = self.validate_basic(node.right, context)
                assert_numeric(lt)
                assert_numeric(rt)
                return DataType.NUMERIC

            case Not():
                assert_boolean(self.validate_basic(node.this, context))
                return DataType.BOOLEAN

            case Count():
                self._validate_aggregate_context(context)
                arg = node.this
                if not isinstance(arg, Star):
                    self.validate(arg, context.enter_aggregate())
                return DataType.INTEGER

            case Avg() | Sum():
                self._validate_aggregate_context(context)
                assert_numeric(self.validate_basic(node.this, context.enter_aggregate()))
                return DataType.NUMERIC

            case Min() | Max():
                self._validate_aggregate_context(context)
                t = self.validate_basic(node.this, context.enter_aggregate())
                assert_orderable(t)
                return t

            case Star():
                return self._validate_star_expansion()

            case Subquery():
                sub_schema = self.query_validator.validate(node.this, self.scope).schema
                try:
                    assert_scalar_subquery(node)
                    [(_, columns)] = sub_schema.items()
                    [(_, t)] = columns.items()
                except ValueError:  # Unpack error
                    # Subquery must return a single table with a single column
                    raise ScalarSubqueryError() from None
                return t

            case In():
                lt = self.validate_basic(node.this, context)
                if subquery := node.args.get('query'):
                    rt = self._validate_quantified_predicate_query(subquery.this)
                    assert_comparable(lt, rt)
                else:
                    # If the IN clause is not a subquery, it must be a list of literals
                    for val in node.expressions:
                        rt = self.validate_basic(val, context)
                        assert_comparable(lt, rt)
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

            case _:
                raise NotImplementedError(f'Expression {type(node)} not supported')

    # ──────── Column Validations ────────

    def _validate_column(self, column: Column, context: ValidationContext) -> DataType:
        t: DataType | None = None
        if t := self.scope.tables.resolve_column(column):
            return t
        else:
            raise UndefinedColumnError(column.name, column.table)

    # ──────── Aggregate Validations ────────

    def _validate_aggregate_context(self, context: ValidationContext) -> None:
        # Cannot be used in the WHERE clause
        if context.in_where:
            raise AggregateInWhereError()
        # Cannot be nested
        if context.in_aggregate:
            raise NestedAggregateError()

    # ──────── Quantified Predicate Validations ────────

    def _validate_quantified_predicate_query(self, query: Expression) -> DataType:
        schema = self.query_validator.validate(query, self.scope).schema
        try:
            [(_, columns)] = schema.items()
            [(_, rt)] = columns.items()
        except ValueError:  # Unpack error
            raise ColumnCountMismatchError(1, len(columns)) from None
        return rt

    # ──────── Star Expansion Validations ────────

    def _validate_star_expansion(self, table: str | None = None) -> ResultSchema:
        schema = (
            self.scope.tables.get_table_schema(table) if table else self.scope.tables.get_schema()
        )

        if self.scope.is_grouped:
            missing: list[str] = []
            for table, table_schema in schema.items():
                for col, _ in table_schema.items():
                    col_expr = Column(this=col, table=table)
                    if not self.scope.group_by.contains(col_expr):
                        missing.append(col)

            if missing:
                raise NonGroupedColumnError(missing)

        return schema
