from queries.services.ra.parser.ast import (
    Attribute,
    RAQuery,
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

    def transpile(self, join_query: RAQuery) -> tuple[RAQuery, list[Attribute]]:
        assert self.scope.where

        subquery_free, exists, not_exists = self._split_condition(self.scope.where.this)

        subquery_free_context_relations: list[RAQuery] = []
        subquery_free_parameters: list[Attribute] = []
        if subquery_free:
            (
                subquery_free_context_relations,
                subquery_free_parameters,
            ) = ContextRelationInferrer(self.scope).infer(subquery_free)

        transpiled_not_exists = [self._transpile_exists(expr) for expr in not_exists]
        not_exists_context_relations = [
            relation for _, relations, _ in transpiled_not_exists for relation in relations
        ]

        transpiled_exists = [self._transpile_exists(expr) for expr in exists]
        exists_context_relations = [
            relation for _, relations, _ in transpiled_exists for relation in relations
        ]

        output_relation = cartesian(
            [
                relation
                for relation in unnest_cartesian_operands(join_query)
                + subquery_free_context_relations
                + not_exists_context_relations
                if relation not in exists_context_relations
            ]
        )

        output_relation = natural_join(
            ([output_relation] if output_relation else [])
            + [subquery.project(parameters) for subquery, _, parameters in transpiled_exists]
        )

        if subquery_free:
            output_relation = output_relation.select(self.expr_transpiler.transpile(subquery_free))

        return output_relation, subquery_free_parameters

    def _split_condition(
        self, condition: Expression
    ) -> tuple[Expression | None, list[Exists], list[Exists]]:
        # Assume one top-level AND
        def extract_predicates(expr: Expression) -> list[Expression]:
            if isinstance(expr, And):
                return extract_predicates(expr.left) + extract_predicates(expr.right)
            return [expr]

        predicates = extract_predicates(condition)

        exists = [p for p in predicates if isinstance(p, Exists)]
        not_exists = [
            p.this for p in predicates if isinstance(p, Not) and isinstance(p.this, Exists)
        ]
        subquery_free = [p for p in predicates if p not in exists and p not in not_exists]

        # Combine subquery-free predicates into a single AND expression
        combined = and_(*subquery_free) if subquery_free else None

        return combined, exists, not_exists

    def _transpile_exists(self, exists: Exists) -> tuple[RAQuery, list[RAQuery], list[Attribute]]:
        from .query import QueryTranspiler

        subquery = exists.this
        scope = self.scope.subquery_scopes[subquery]
        context_relations, parameters = ContextRelationInferrer(scope).infer(subquery)

        return QueryTranspiler.transpile(scope), context_relations, parameters
