from queries.services.ra.parser.ast import SetOperation as RASetOperation
from sqlglot.expressions import Except, Intersect, Union

from ..scope.query import SetOperationScope


class SetOperationTranspiler:
    @staticmethod
    def transpile(scope: SetOperationScope) -> RASetOperation:
        from .query import QueryTranspiler

        left = QueryTranspiler.transpile(scope.left)
        right = QueryTranspiler.transpile(scope.right)

        match scope.set_operation:
            case Union():
                return left.union(right)
            case Intersect():
                return left.intersect(right)
            case Except():
                return left.difference(right)
            case _:
                raise NotImplementedError(f'Unsupported set operation: {type(scope.set_operation)}')
