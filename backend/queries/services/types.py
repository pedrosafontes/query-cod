from databases.types import Columns, Schema
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import DataType as SQLGlotDataType


RelationName = str
AttributeName = str
Attributes = dict[AttributeName, DataType]
RelationalSchema = dict[RelationName | None, Attributes]


def merge_common_column(result_schema: RelationalSchema, col: str) -> None:
    types = []
    for schema in result_schema.values():
        if col in schema:
            types.append(schema.pop(col))
    result_schema.setdefault(None, {})[col] = DataType.dominant(types)


def flatten(schema: RelationalSchema) -> Attributes:
    flat: Attributes = {}
    for attributes in schema.values():
        for attr, t in attributes.items():
            flat[attr] = t
    return flat


def to_relational_schema(schema: Schema) -> RelationalSchema:
    return {name: _columns_to_attributes(columns) for name, columns in schema.items()}


def _columns_to_attributes(columns: Columns) -> Attributes:
    return {name: col['type'] for name, col in columns.items()}


def _data_type_to_sqlglot_type(data_type: DataType) -> SQLGlotDataType:
    match data_type:
        case DataType.SMALLINT:
            return SQLGlotDataType.build('SMALLINT')
        case DataType.INTEGER:
            return SQLGlotDataType.build('INTEGER')
        case DataType.DECIMAL:
            return SQLGlotDataType.build('DECIMAL(10, 0)')
        case DataType.NUMERIC:
            return SQLGlotDataType.build('NUMERIC(10, 0)')
        case DataType.REAL:
            return SQLGlotDataType.build('REAL')
        case DataType.FLOAT:
            return SQLGlotDataType.build('FLOAT')
        case DataType.DOUBLE_PRECISION:
            return SQLGlotDataType.build('DOUBLE_PRECISION')

        case DataType.CHAR:
            return SQLGlotDataType.build('CHAR(1)')
        case DataType.VARCHAR:
            return SQLGlotDataType.build('TEXT')

        case DataType.BIT:
            return SQLGlotDataType.build('BIT(1)')
        case DataType.BIT_VARYING:
            return SQLGlotDataType.build('BIT_VARYING(255)')

        case DataType.DATE:
            return SQLGlotDataType.build('DATE')
        case DataType.TIME:
            return SQLGlotDataType.build('TIME')
        case DataType.TIMESTAMP:
            return SQLGlotDataType.build('TIMESTAMP')

        case DataType.BOOLEAN:
            return SQLGlotDataType.build('BOOLEAN')

        case _:
            raise ValueError(f'Unsupported data type: {data_type}')


def to_sqlglot_schema(schema: RelationalSchema) -> dict[str, dict[str, SQLGlotDataType]]:
    return {
        table_name: {
            column_name: _data_type_to_sqlglot_type(data_type)
            for column_name, data_type in columns.items()
        }
        for table_name, columns in schema.items()
        if table_name
    }
