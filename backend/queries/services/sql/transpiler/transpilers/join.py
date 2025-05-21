from queries.services.ra.parser.ast import (
    Join,
    JoinOperator,
    RAQuery,
    SetOperation,
    SetOperator,
    ThetaJoin,
)
from sqlglot.expressions import Expression
from sqlglot.expressions import Join as SQLJoin

from .expression import ExpressionTranspiler
from .table import TableTranspiler


class JoinTranspiler:
    @staticmethod
    def transpile(join: SQLJoin, left: RAQuery) -> RAQuery:
        right = TableTranspiler.transpile(join.this)

        kind = join.method or join.args.get('kind', 'INNER')
        using = join.args.get('using')
        condition = join.args.get('on')

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
        else:
            assert isinstance(condition, Expression)
            return ThetaJoin(
                left=left,
                right=right,
                condition=ExpressionTranspiler.transpile(condition),
            )

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
