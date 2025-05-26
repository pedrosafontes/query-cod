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


def transpile_set_operation(scope: SetOperationScope) -> RASetOperation:
    left, l_context_relations, l_parameters = transpile_operand(scope.left)
    right, r_context_relations, r_parameters = transpile_operand(scope.right)

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


def transpile_operand(scope: SQLScope) -> tuple[RAQuery, set[RAQuery], list[Attribute]]:
    from .query import transpile_query

    context_relations, parameters = ContextRelationInferrer(scope).infer(scope.query)

    return transpile_query(scope), set(context_relations), parameters
