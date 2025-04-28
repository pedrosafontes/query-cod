from queries.services.ra.parser.ast import AggregationFunction, ComparisonValue
from ra_sql_visualisation.types import DataType


def type_of_function(
    func: AggregationFunction, input_type: DataType
) -> tuple[list[DataType], DataType]:
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
