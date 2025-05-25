from queries.services.ra.parser.ast import (
    Attribute,
    RAQuery,
    cartesian,
)
from queries.services.ra.parser.ast import (
    SetOperation as RASetOperation,
)
from queries.services.sql.transpiler.context import ContextRelationInferrer
from sqlglot.expressions import Except, Intersect, Union

from ..scope.query import SetOperationScope, SQLScope


class SetOperationTranspiler:
    @staticmethod
    def transpile(scope: SetOperationScope) -> RASetOperation:
        left, l_context_relations, l_parameters = SetOperationTranspiler.transpile_operand(
            scope.left
        )
        right, r_context_relations, r_parameters = SetOperationTranspiler.transpile_operand(
            scope.right
        )

        parameters = list(set(l_parameters) | set(r_parameters))

        if parameters:
            left = cartesian([left, *(r_context_relations - l_context_relations)]).project(
                parameters, append=True
            )
            right = cartesian([right, *(l_context_relations - r_context_relations)]).project(
                parameters, append=True
            )

        match scope.set_operation:
            case Union():
                return left.union(right)
            case Intersect():
                return left.intersect(right)
            case Except():
                return left.difference(right)
            case _:
                raise NotImplementedError(f'Unsupported set operation: {type(scope.set_operation)}')

    @staticmethod
    def transpile_operand(scope: SQLScope) -> tuple[RAQuery, set[RAQuery], list[Attribute]]:
        from .query import QueryTranspiler

        context_relations, parameters = ContextRelationInferrer(scope).infer(scope.query)
        transpiled_query = QueryTranspiler.transpile(scope)

        return transpiled_query, set(context_relations), parameters
