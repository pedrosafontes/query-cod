from databases.types import DataType

from ..parser.ast import AggregationFunction, ComparisonValue
from .types import TypedAttribute


def type_of_function(
    func: AggregationFunction, attr: TypedAttribute
) -> tuple[list[DataType], DataType]:
    input_type = attr.data_type
    match func:
        case AggregationFunction.COUNT:
            return ([input_type], DataType.INTEGER)
        case AggregationFunction.SUM | AggregationFunction.AVG:
            return ([DataType.INTEGER, DataType.FLOAT], DataType.FLOAT)
        case AggregationFunction.MIN | AggregationFunction.MAX:
            return ([input_type], input_type)
        case _:
            raise NotImplementedError(f'Unknown aggregation function: {func}')


def type_of_value(value: ComparisonValue) -> DataType:
    match value:
        case int():
            return DataType.INTEGER
        case float():
            return DataType.FLOAT
        case str():
            return DataType.VARCHAR
        case bool():
            return DataType.BOOLEAN
        case _:
            raise NotImplementedError(f'Unknown type: {type(value)}')
