from queries.services.ra.parser.ast import SetOperation as RASetOperation
from queries.services.ra.parser.ast import SetOperator
from queries.services.sql.scope.query import SetOperationScope
from sqlglot.expressions import Except, Intersect, Union


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
