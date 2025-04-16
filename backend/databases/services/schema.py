from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.types import Schema
from sqlalchemy import inspect


def get_schema(db: DatabaseConnectionInfo) -> Schema:
    engine = db.to_sqlalchemy_engine()
    inspector = inspect(engine)
    schema = {
        table: {col['name']: col['type'] for col in inspector.get_columns(table)}
        for table in inspector.get_table_names()
    }
    return schema
