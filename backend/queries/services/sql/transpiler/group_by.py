from collections import defaultdict

from queries.services.ra.parser.ast import Aggregation, GroupedAggregation, RAQuery
from sqlglot.expressions import Column

from ..scope.query import SelectScope
from ..types import AggregateFunction, aggregate_functions
from .expression import ExpressionTranspiler
from .utils import convert_sqlglot_aggregation_function


class GroupByTranspiler:
    def __init__(self) -> None:
        self._alias_counts: dict[str, int] = defaultdict(int)
        self.aggregates: dict[AggregateFunction, str] = {}

    def transpile(self, scope: SelectScope, subquery: RAQuery) -> RAQuery:
        group_by = []
        if scope.group:
            for expr in scope.group.expressions:
                if isinstance(expr, Column):
                    group_by.append(ExpressionTranspiler.transpile_column(expr))
                else:
                    raise NotImplementedError(f'Unsupported GROUP BY expression: {type(expr)}')

        self._extract_having_aggregations(scope)
        self._extract_select_aggregations(scope)

        aggregations = [
            self._transpile_aggregation(aggregate, output)
            for aggregate, output in self.aggregates.items()
        ]

        if aggregations:
            return GroupedAggregation(
                group_by=group_by,
                aggregations=aggregations,
                subquery=subquery,
            )
        else:
            return subquery

    def _transpile_aggregation(self, aggregate: AggregateFunction, output: str) -> Aggregation:
        attr = aggregate.this
        if isinstance(attr, Column):
            attr = ExpressionTranspiler.transpile_column(attr)
            return Aggregation(
                input=attr,
                aggregation_function=convert_sqlglot_aggregation_function(aggregate),
                output=output,
            )
        else:
            raise NotImplementedError(f'Unsupported aggregation expression: {type(attr)}')

    def _extract_having_aggregations(self, scope: SelectScope) -> None:
        if scope.having:
            for aggregate in scope.having.this.find_all(*aggregate_functions):
                self._add_aggregate(aggregate)

    def _extract_select_aggregations(self, scope: SelectScope) -> None:
        for select_item in scope.select.expressions:
            expr = select_item.this
            if isinstance(expr, AggregateFunction):
                self._add_aggregate(expr, select_item.alias)

    def _add_aggregate(self, aggregate: AggregateFunction, alias: str | None = None) -> None:
        if not alias:
            func_name = aggregate.key.upper()
            self._alias_counts[func_name] += 1
            alias = f'{func_name.lower()}_{self._alias_counts[func_name]}'

        self.aggregates[aggregate] = alias
