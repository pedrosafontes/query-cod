from collections.abc import Callable

from queries.services.ra.ast import (
    Division,
    GroupedAggregation,
    Join,
    Projection,
    RAQuery,
    Relation,
    Rename,
    Selection,
    SetOperation,
    ThetaJoin,
    TopN,
)
from queries.services.types import RelationalSchema
from queries.types import QueryError

from ..latex import converter as latex_converter
from ..latex.utils import (
    text,
)
from ..semantics import validate_ra_semantics
from .types import (
    DivisionNode,
    GroupedAggregationNode,
    JoinNode,
    ProjectionNode,
    RATree,
    RelationNode,
    RenameNode,
    SelectionNode,
    SetOperationNode,
    ThetaJoinNode,
    TopNNode,
)


class RATreeBuilder:
    _counter: int
    _subqueries: dict[int, RAQuery]

    def __init__(self, schema: RelationalSchema):
        self._schema = schema

    def build(self, query: RAQuery) -> tuple[RATree, dict[int, RAQuery]]:
        self._counter = 0
        self._subqueries = {}
        return self._build(query), self._subqueries

    def _add_subquery(self, subquery: RAQuery) -> tuple[int, list[QueryError]]:
        query_id = self._counter
        errors = validate_ra_semantics(subquery, self._schema)
        self._counter += 1
        self._subqueries[query_id] = subquery
        return query_id, errors

    def _build(self, query: RAQuery) -> RATree:
        method: Callable[[RAQuery], RATree] = getattr(self, f'_build_{type(query).__name__}')
        return method(query)

    def _build_Relation(self, rel: Relation) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(rel)
        return RelationNode(
            id=query_id, validation_errors=errors, name=text(rel.name), children=None
        )

    def _build_Projection(self, proj: Projection) -> ProjectionNode:  # noqa: N802
        attributes = [latex_converter.convert_attribute(attr) for attr in proj.attributes]
        query_id, errors = self._add_subquery(proj)
        return ProjectionNode(
            id=query_id,
            validation_errors=errors,
            attributes=attributes,
            children=[self._build(proj.subquery)],
        )

    def _build_Selection(self, sel: Selection) -> SelectionNode:  # noqa: N802
        query_id, errors = self._add_subquery(sel)
        return SelectionNode(
            id=query_id,
            validation_errors=errors,
            condition=latex_converter.convert_condition(sel.condition),
            children=[self._build(sel.subquery)],
        )

    def _build_Rename(self, rename: Rename) -> RenameNode:  # noqa: N802
        query_id, errors = self._add_subquery(rename)
        return RenameNode(
            id=query_id,
            validation_errors=errors,
            alias=text(rename.alias),
            children=[self._build(rename.subquery)],
        )

    def _build_Division(self, div: Division) -> RATree:  # noqa: N802
        query_id, errors = self._add_subquery(div)
        return DivisionNode(
            id=query_id,
            validation_errors=errors,
            children=[self._build(div.dividend), self._build(div.divisor)],
        )

    def _build_SetOperation(self, set_op: SetOperation) -> SetOperationNode:  # noqa: N802
        query_id, errors = self._add_subquery(set_op)
        return SetOperationNode(
            id=query_id,
            validation_errors=errors,
            operator=set_op.operator.value,
            children=[self._build(set_op.left), self._build(set_op.right)],
        )

    def _build_Join(self, join: Join) -> JoinNode:  # noqa: N802
        query_id, errors = self._add_subquery(join)
        return JoinNode(
            id=query_id,
            validation_errors=errors,
            operator=join.operator.value,
            children=[self._build(join.left), self._build(join.right)],
        )

    def _build_ThetaJoin(self, join: ThetaJoin) -> ThetaJoinNode:  # noqa: N802
        query_id, errors = self._add_subquery(join)
        return ThetaJoinNode(
            id=query_id,
            validation_errors=errors,
            condition=latex_converter.convert_condition(join.condition),
            children=[self._build(join.left), self._build(join.right)],
        )

    def _build_GroupedAggregation(self, agg: GroupedAggregation) -> GroupedAggregationNode:  # noqa: N802
        group_by = [latex_converter.convert_attribute(attr) for attr in agg.group_by]
        aggregations = [
            (
                latex_converter.convert_attribute(a.input),
                a.aggregation_function.value.lower(),
                text(a.output),
            )
            for a in agg.aggregations
        ]

        query_id, errors = self._add_subquery(agg)
        return GroupedAggregationNode(
            id=query_id,
            validation_errors=errors,
            group_by=group_by,
            aggregations=aggregations,
            children=[self._build(agg.subquery)],
        )

    def _build_TopN(self, top_n: TopN) -> TopNNode:  # noqa: N802
        query_id, errors = self._add_subquery(top_n)
        return TopNNode(
            id=query_id,
            validation_errors=errors,
            limit=top_n.limit,
            attribute=latex_converter.convert_attribute(top_n.attribute),
            children=[self._build(top_n.subquery)],
        )
