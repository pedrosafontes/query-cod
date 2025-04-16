from typing import Any

from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.types import DataType, Schema
from sqlalchemy import Boolean, Date, Integer, Numeric, String, inspect


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


def _sqlalchemy_type_to_data_type(sqlatype: Any) -> DataType:
    if isinstance(sqlatype, Integer):
        return DataType.INTEGER
    if isinstance(sqlatype, Numeric):
        return DataType.FLOAT
    if isinstance(sqlatype, String):
        return DataType.STRING
    if isinstance(sqlatype, Boolean):
        return DataType.BOOLEAN
    if isinstance(sqlatype, Date):
        return DataType.DATE
    return DataType.UNKNOWN
