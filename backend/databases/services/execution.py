from databases.models import DatabaseConnectionInfo
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text


def execute_sql(sql: str, db: DatabaseConnectionInfo) -> dict:
    engine = create_engine(_build_url(db))

    with engine.connect() as conn:
        result = conn.execute(sql_text(sql))
        rows = result.fetchall()
        columns = result.keys()
        return {
            'columns': columns,
            'rows': [list(row) for row in rows],
        }


def _build_url(db: DatabaseConnectionInfo) -> str:
    match db.type:
        case 'postgresql':
            return f'postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}'
        case _:
            raise ValueError(f'Unsupported database type: {db.type}')
