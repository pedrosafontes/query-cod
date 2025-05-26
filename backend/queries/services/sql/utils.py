from query_cod.types import DataType
from sqlglot.expressions import DataType as SQLGLotDataType


def convert_sqlglot_type(sqlglot_type: SQLGLotDataType) -> DataType:
    type_mapping = {
        SQLGLotDataType.Type.BOOLEAN: DataType.BOOLEAN,
        SQLGLotDataType.Type.CHAR: DataType.CHAR,
        SQLGLotDataType.Type.VARCHAR: DataType.VARCHAR,
        SQLGLotDataType.Type.TEXT: DataType.VARCHAR,
        SQLGLotDataType.Type.INT: DataType.INTEGER,
        SQLGLotDataType.Type.BIGINT: DataType.INTEGER,
        SQLGLotDataType.Type.SMALLINT: DataType.SMALLINT,
        SQLGLotDataType.Type.FLOAT: DataType.FLOAT,
        SQLGLotDataType.Type.DOUBLE: DataType.DOUBLE_PRECISION,
        SQLGLotDataType.Type.DECIMAL: DataType.DECIMAL,
        SQLGLotDataType.Type.DATE: DataType.DATE,
        SQLGLotDataType.Type.TIME: DataType.TIME,
        SQLGLotDataType.Type.TIMESTAMP: DataType.TIMESTAMP,
        SQLGLotDataType.Type.BIT: DataType.BIT,
    }

    base_type = sqlglot_type.this
    if base_type not in type_mapping:
        raise ValueError(f'Unsupported SQLGlot type: {base_type}')

    return type_mapping[base_type]
