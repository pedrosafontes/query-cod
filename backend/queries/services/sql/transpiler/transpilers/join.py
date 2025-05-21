from queries.services.ra.parser.ast import (
    Join,
    JoinOperator,
    RAQuery,
    SetOperation,
    SetOperator,
    ThetaJoin,
)
from queries.services.sql.scope.query import SelectScope
from sqlglot.expressions import Expression
from sqlglot.expressions import Join as SQLJoin

from .expression import ExpressionTranspiler
from .table import TableTranspiler


class JoinTranspiler:
    def __init__(self, scope: SelectScope):
        self.scope = scope
        self.table_transpiler = TableTranspiler(scope)

    def transpile(self, join: SQLJoin, left: RAQuery) -> RAQuery:
        right = self.table_transpiler.transpile(join.this)

        kind = join.method or join.args.get('kind', 'INNER')
        using = join.args.get('using')
        condition: Expression | None = join.args.get('on')

        if using:
            raise NotImplementedError('USING clause is not supported yet')
        elif kind == 'NATURAL':
            return Join(
                operator=JoinOperator.NATURAL,
                left=left,
                right=right,
            )
        elif kind == 'CROSS':
            return SetOperation(
                operator=SetOperator.CARTESIAN,
                left=left,
                right=right,
            )
        elif condition:
            return ThetaJoin(
                left=left,
                right=right,
                condition=ExpressionTranspiler.transpile(condition),
            )
        else:
            raise ValueError('Invalid JOIN clause')

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
