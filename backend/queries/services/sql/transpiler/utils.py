from queries.services.ra.parser.ast import AggregationFunction
from sqlglot.expressions import Avg, Count, Max, Min, Sum

from ..types import AggregateFunction


def convert_sqlglot_aggregation_function(
    func: AggregateFunction,
) -> AggregationFunction:
    match func:
        case Count():
            return AggregationFunction.COUNT
        case Sum():
            return AggregationFunction.SUM
        case Avg():
            return AggregationFunction.AVG
        case Min():
            return AggregationFunction.MIN
        case Max():
            return AggregationFunction.MAX
