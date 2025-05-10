from collections.abc import Callable

from queries.services.ra.parser.ast import (
    Division,
    GroupedAggregation,
    Join,
    Projection,
    RAQuery,
    Relation,
    Selection,
    SetOperation,
    ThetaJoin,
    TopN,
)


class RASubqueryExtractor:
    _counter: int
    _subqueries: dict[int, RAQuery]

    def extract(self, query: RAQuery) -> dict[int, RAQuery]:
        self._counter = 0
        self._subqueries = {}
        self._extract(query)
        return self._subqueries

    def _extract(self, query: RAQuery) -> None:
        next_id = self._counter
        self._counter += 1
        method: Callable[[RAQuery, int], None] = getattr(self, f'_extract_{type(query).__name__}')
        method(query, next_id)

    def _extract_Relation(self, rel: Relation, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = rel

    def _extract_Projection(self, proj: Projection, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = proj
        self._extract(proj.subquery)

    def _extract_Selection(self, sel: Selection, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = sel
        self._extract(sel.subquery)

    def _extract_Division(self, div: Division, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = div
        self._extract(div.dividend)
        self._extract(div.divisor)

    def _extract_SetOperation(self, set_op: SetOperation, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = set_op
        self._extract(set_op.left)
        self._extract(set_op.right)

    def _extract_Join(self, join: Join, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = join
        self._extract(join.left)
        self._extract(join.right)

    def _extract_ThetaJoin(self, join: ThetaJoin, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = join
        self._extract(join.left)
        self._extract(join.right)

    def _extract_GroupedAggregation(self, agg: GroupedAggregation, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = agg
        self._extract(agg.subquery)

    def _extract_TopN(self, top_n: TopN, node_id: int) -> None:  # noqa: N802
        self._subqueries[node_id] = top_n
        self._extract(top_n.subquery)
