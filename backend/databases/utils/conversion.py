from databases.models import Database, DatabaseConnectionInfo


def from_model(database: Database) -> DatabaseConnectionInfo:
    return DatabaseConnectionInfo(
        database_type=database.database_type,
        host=database.host,
        port=database.port,
        user=database.user,
        password=database.password,
        name=database.database_name,
    )
