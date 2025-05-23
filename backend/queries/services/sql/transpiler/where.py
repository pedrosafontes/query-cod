from queries.services.ra.parser.ast import (
    Attribute,
    RAQuery,
    SetOperation,
    SetOperator,
    cartesian,
    natural_join,
)
from sqlglot.expressions import And, Column, Exists, Expression, Not, Table, and_

from ..scope.query import SelectScope, SQLScope
from ..scope.tables import Source
from .expression import ExpressionTranspiler
from .table import TableTranspiler


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
            ) = WhereTranspiler._get_context_relations(self.scope, subquery_free)

        transpiled_not_exists = [self._transpile_exists(expr) for expr in not_exists]
        not_exists_context_relations = [
            relation for _, relations, _ in transpiled_not_exists for relation in relations
        ]

        transpiled_exists = [self._transpile_exists(expr) for expr in exists]
        exists_context_relations = [
            relation for _, relations, _ in transpiled_exists for relation in relations
        ]

        def extract_relations(query: RAQuery) -> list[RAQuery]:
            match query:
                case SetOperation(operator=SetOperator.CARTESIAN):
                    return extract_relations(query.left) + extract_relations(query.right)
                case _:
                    return [query]

        output_relation = cartesian(
            [
                relation
                for relation in extract_relations(join_query)
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
            match expr:
                case And():
                    return extract_predicates(expr.left) + extract_predicates(expr.right)
                case _:
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
        context_relations, parameters = WhereTranspiler._get_context_relations(scope, subquery)

        return QueryTranspiler.transpile(scope), context_relations, parameters

    @staticmethod
    def _get_context_relations(
        scope: SQLScope, expr: Expression
    ) -> tuple[list[RAQuery], list[Attribute]]:
        sources: list[Source] = []
        for column in expr.find_all(Column):
            if column not in scope.tables and (source := scope.tables.find_column_source(column)):
                sources.append(source)

        relations = [WhereTranspiler._transpile_source(scope, source) for source in sources]
        parameters = [
            Attribute(name=name, relation=source.name)
            for source in sources
            for name in source.attributes
        ]
        return relations, parameters

    @staticmethod
    def _transpile_source(scope: SQLScope, source: Source) -> RAQuery:
        from .query import QueryTranspiler

        match source.table:
            case Table():
                return TableTranspiler(scope).transpile(source.table)
            case SQLScope():
                return QueryTranspiler.transpile(source.table)
