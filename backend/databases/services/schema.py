from typing import Any

from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.types import Schema
from ra_sql_visualisation.types import DataType
from sqlalchemy import (
    CHAR,
    DOUBLE_PRECISION,
    REAL,
    VARCHAR,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    inspect,
)
from sqlalchemy.types import TypeEngine


def get_schema(db: DatabaseConnectionInfo) -> Schema:
    engine = db.to_sqlalchemy_engine()
    inspector = inspect(engine)
    schema = {
        table: {
            col['name']: _sqlalchemy_type_to_data_type(col['type'])
            for col in inspector.get_columns(table)
        }
        for table in inspector.get_table_names()
    }
    return schema


def _sqlalchemy_type_to_data_type(sqlatype: TypeEngine[Any]) -> DataType:
    match sqlatype:
        # Exact numeric types
        case SmallInteger():
            return DataType.SMALLINT
        case Integer():
            return DataType.INTEGER
        case Numeric():
            return DataType.NUMERIC

        # Approximate numeric types
        case Float():
            return DataType.FLOAT
        case REAL():
            return DataType.REAL
        case DOUBLE_PRECISION():
            return DataType.DOUBLE_PRECISION

        # Character string types
        case CHAR():
            return DataType.CHAR
        case VARCHAR():
            return DataType.VARCHAR
        case String() | Text():
            return DataType.VARCHAR  # Defaulting to VARCHAR for general string types

        # Boolean type
        case Boolean():
            return DataType.BOOLEAN

        # Date/time types
        case Date():
            return DataType.DATE
        case Time():
            return DataType.TIME
        case DateTime():
            return DataType.TIMESTAMP
        case _:
            raise ValueError(f'Unsupported SQLAlchemy type: {sqlatype}')
