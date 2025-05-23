from queries.services.ra.parser.ast import (
    RAQuery,
)
from sqlglot.expressions import Expression
from sqlglot.expressions import Join as SQLJoin

from ..scope.query import SelectScope
from .expression import ExpressionTranspiler
from .table import TableTranspiler


class JoinTranspiler:
    def __init__(self, scope: SelectScope):
        self.scope = scope
        self.table_transpiler = TableTranspiler(scope)
        self.expr_transpiler = ExpressionTranspiler(scope)

    def transpile(self, join: SQLJoin, left: RAQuery) -> RAQuery:
        right = self.table_transpiler.transpile(join.this)

        using = join.args.get('using')
        condition: Expression | None = join.args.get('on')

        if using:
            raise NotImplementedError('USING clause is not supported yet')
        elif condition:
            return left.theta_join(right, self.expr_transpiler.transpile(condition))
        else:
            return left.natural_join(right)

    # def _validate_using(
    #     self, using: list[Identifier], left: Attributes, right: Attributes, join: Join
    # ) -> None:
    #     # All columns in USING must be present in both tables
    #     for ident in using:
    #         col = ident.name
    #         if col not in left:
    #             raise ColumnNotFoundError.from_expression(join, col)
    #         assert_comparable(left[col], right[col], join)
    #         self.scope.tables.merge_common_column(col)
