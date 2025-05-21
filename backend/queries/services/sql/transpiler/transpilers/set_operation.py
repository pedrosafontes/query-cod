from queries.services.ra.parser.ast import SetOperation as RASetOperation
from queries.services.ra.parser.ast import SetOperator
from sqlglot.expressions import Except, Intersect, SetOperation, Union


class SetOperationTranspiler:
    @staticmethod
    def transpile(set_operation: SetOperation) -> RASetOperation:
        from .query import SQLtoRATranspiler

        operators = {
            Union: SetOperator.UNION,
            Intersect: SetOperator.INTERSECT,
            Except: SetOperator.DIFFERENCE,
        }

        return RASetOperation(
            operator=operators[type(set_operation)],
            left=SQLtoRATranspiler.transpile(set_operation.left),
            right=SQLtoRATranspiler.transpile(set_operation.right),
        )
