from queries.services.ra.parser.ast import ComparisonValue
from ra_sql_visualisation.types import DataType


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
