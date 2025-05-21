from collections import defaultdict

from queries.services.ra.parser.ast import Aggregation, GroupedAggregation, RAQuery
from sqlglot.expressions import Column, Select

from ..types import AggregateFunction, aggregate_functions
from .expression import ExpressionTranspiler
from .utils import convert_sqlglot_aggregation_function


class GroupByTranspiler:
    def __init__(self) -> None:
        self._alias_counts: dict[str, int] = defaultdict(int)
        self.aggregates: dict[AggregateFunction, str] = {}

    def transpile(self, query: Select, subquery: RAQuery) -> RAQuery:
        group_by = []
        if group := query.args.get('group'):
            for expr in group.expressions:
                if isinstance(expr, Column):
                    group_by.append(ExpressionTranspiler.transpile_column(expr))
                else:
                    raise NotImplementedError(f'Unsupported GROUP BY expression: {type(expr)}')

        self._extract_having_aggregations(query)
        self._extract_select_aggregations(query)

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

    def _extract_having_aggregations(self, query: Select) -> None:
        having = query.args.get('having')
        if having:
            for aggregate in having.this.find_all(*aggregate_functions):
                self._add_aggregate(aggregate)

    def _extract_select_aggregations(self, select: Select) -> None:
        for select_item in select.expressions:
            expr = select_item.this
            if isinstance(expr, AggregateFunction):
                self._add_aggregate(expr, select_item.alias)

    def _add_aggregate(self, aggregate: AggregateFunction, alias: str | None = None) -> None:
        if not alias:
            func_name = aggregate.key.upper()
            self._alias_counts[func_name] += 1
            alias = f'{func_name.lower()}_{self._alias_counts[func_name]}'

        self.aggregates[aggregate] = alias
