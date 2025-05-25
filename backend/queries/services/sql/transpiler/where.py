from collections.abc import Callable

from queries.services.ra.parser.ast import (
    Attribute,
    RAQuery,
    anti_join,
    cartesian,
    natural_join,
    unnest_cartesian_operands,
)
from sqlglot.expressions import And, Exists, Expression, Not, and_

from ..scope.query import SelectScope
from .context import ContextRelationInferrer
from .expression import ExpressionTranspiler


class WhereTranspiler:
    def __init__(self, scope: SelectScope):
        self.scope = scope
        self.expr_transpiler = ExpressionTranspiler(scope)
        self.parameters: list[Attribute] = []

    def transpile(self, join_query: RAQuery) -> RAQuery:
        assert self.scope.where  # noqa: S101

        subquery_free, exists, not_exists = self._split_condition(self.scope.where.this)

        context_relations, parameters = (
            ContextRelationInferrer(self.scope).infer(subquery_free) if subquery_free else ([], [])
        )
        self.parameters = parameters

        transpiled_not_exists = [self._transpile_exists(expr) for expr in not_exists]
        not_exists_context_relations = self._all_context_relations(transpiled_not_exists)

        transpiled_exists = [self._transpile_exists(expr) for expr in exists]
        exists_context_relations = self._all_context_relations(transpiled_exists)

        from_and_context = [
            relation
            for relation in unnest_cartesian_operands(join_query)
            + context_relations
            + not_exists_context_relations
            if relation not in exists_context_relations
        ]

        result = cartesian(from_and_context) if from_and_context else None
        result = self._perform_decorrelation(natural_join, result, transpiled_exists)
        result = self._perform_decorrelation(anti_join, result, transpiled_not_exists)

        assert result  # noqa: S101

        if subquery_free:
            result = result.select(self.expr_transpiler.transpile(subquery_free))

        return result

    def _split_condition(
        self, condition: Expression
    ) -> tuple[Expression | None, list[Exists], list[Exists]]:
        # Assume one top-level AND
        predicates = list(condition.flatten()) if isinstance(condition, And) else [condition]  # type: ignore[no-untyped-call]

        exists = [p for p in predicates if isinstance(p, Exists)]
        not_exists = [
            p.this for p in predicates if isinstance(p, Not) and isinstance(p.this, Exists)
        ]
        other = [p for p in predicates if p not in exists and p not in not_exists]

        # Combine subquery-free predicates into a single AND expression
        subquery_free = and_(*other) if other else None

        return subquery_free, exists, not_exists

    def _transpile_exists(self, exists: Exists) -> tuple[RAQuery, list[RAQuery], list[Attribute]]:
        from .query import QueryTranspiler

        subquery = exists.this
        scope = self.scope.subquery_scopes[subquery]
        context_relations, parameters = ContextRelationInferrer(scope).infer(subquery)

        return QueryTranspiler.transpile(scope), context_relations, parameters

    def _all_context_relations(
        self, transpiled_exists: list[tuple[RAQuery, list[RAQuery], list[Attribute]]]
    ) -> list[RAQuery]:
        return [
            relation
            for _, context_relations, _ in transpiled_exists
            for relation in context_relations
        ]

    def _perform_decorrelation(
        self,
        join: Callable[[list[RAQuery]], RAQuery],
        left: RAQuery | None,
        transpiled_exists: list[tuple[RAQuery, list[RAQuery], list[Attribute]]],
    ) -> RAQuery | None:
        relations = ([left] if left else []) + [
            subquery.project(parameters) for subquery, _, parameters in transpiled_exists
        ]
        return join(relations) if relations else None
