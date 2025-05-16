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
    def transpile(self, join: SQLJoin, left: RAQuery) -> RAQuery:
        right = TableTranspiler().transpile(join.this)

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
                condition=ExpressionTranspiler().transpile(condition),
            )
