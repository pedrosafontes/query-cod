from collections import defaultdict

from queries.services.ra.parser.ast import Aggregation, GroupedAggregation, RAQuery
from sqlglot.expressions import Column

from ..scope.query import SelectScope
from ..types import AggregateFunction, aggregate_functions
from .expression import ExpressionTranspiler
from .utils import convert_sqlglot_aggregation_function


class GroupByTranspiler:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope
        self.expr_transpiler = ExpressionTranspiler(scope)
        self._alias_counts: dict[str, int] = defaultdict(int)
        self.aggregates: dict[AggregateFunction, str] = {}

    def transpile(self, subquery: RAQuery) -> RAQuery:
        group_by = []
        if self.scope.group:
            for expr in self.scope.group.expressions:
                if isinstance(expr, Column):
                    group_by.append(self.expr_transpiler.transpile_column(expr))
                else:
                    raise NotImplementedError(f'Unsupported GROUP BY expression: {type(expr)}')

        self._extract_having_aggregations()
        self._extract_select_aggregations()

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
            attr = self.expr_transpiler.transpile_column(attr)
            return Aggregation(
                input=attr,
                aggregation_function=convert_sqlglot_aggregation_function(aggregate),
                output=output,
            )
        else:
            raise NotImplementedError(f'Unsupported aggregation expression: {type(attr)}')

    def _extract_having_aggregations(self) -> None:
        if self.scope.having:
            for aggregate in self.scope.having.this.find_all(*aggregate_functions):
                self._add_aggregate(aggregate)

    def _extract_select_aggregations(self) -> None:
        for select_item in self.scope.select.expressions:
            expr = select_item.this
            if isinstance(expr, AggregateFunction):
                self._add_aggregate(expr, select_item.alias)

    def _add_aggregate(self, aggregate: AggregateFunction, alias: str | None = None) -> None:
        if not alias:
            func_name = aggregate.key.upper()
            self._alias_counts[func_name] += 1
            alias = f'{func_name.lower()}_{self._alias_counts[func_name]}'

        self.aggregates[aggregate] = alias
