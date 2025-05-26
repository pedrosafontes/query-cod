from queries.services.ra.ast import AggregationFunction
from ra_sql_visualisation.types import DataType


def type_of_function(
    func: AggregationFunction, input_type: DataType
) -> tuple[list[DataType], DataType]:
    numeric_types = [dt for dt in DataType if dt.is_numeric()]
    match func:
        case AggregationFunction.COUNT:
            return ([input_type], DataType.INTEGER)
        case AggregationFunction.SUM | AggregationFunction.AVG:
            return (numeric_types, input_type if input_type in numeric_types else DataType.FLOAT)
        case AggregationFunction.MIN | AggregationFunction.MAX:
            return ([input_type], input_type)
        case _:
            raise NotImplementedError(f'Unknown aggregation function: {func}')
