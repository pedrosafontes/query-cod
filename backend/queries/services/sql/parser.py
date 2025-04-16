from databases.models import DatabaseConnectionInfo
from sqlglot import expressions, parse_one


def parse_sql(query_text: str, db: DatabaseConnectionInfo) -> expressions.Select:
    return parse_one(
        query_text,
        read=_database_type_to_sqlglot(db.database_type),
        into=expressions.Select,
    )


def _database_type_to_sqlglot(db_type: str) -> str:
    return {
        'postgresql': 'postgres',
    }.get(db_type, db_type)
