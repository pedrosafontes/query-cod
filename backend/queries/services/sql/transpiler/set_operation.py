from queries.services.ra.parser.ast import SetOperation as RASetOperation
from queries.services.ra.parser.ast import SetOperator
from sqlglot.expressions import Except, Intersect, Union

from ..scope.query import SetOperationScope


class SetOperationTranspiler:
    @staticmethod
    def transpile(scope: SetOperationScope) -> RASetOperation:
        from .query import QueryTranspiler

        operators = {
            Union: SetOperator.UNION,
            Intersect: SetOperator.INTERSECT,
            Except: SetOperator.DIFFERENCE,
        }

        return RASetOperation(
            operator=operators[type(scope.set_operation)],
            left=QueryTranspiler.transpile(scope.left),
            right=QueryTranspiler.transpile(scope.right),
        )
