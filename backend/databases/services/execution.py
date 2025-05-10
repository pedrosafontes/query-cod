from databases.models import DatabaseConnectionInfo
from databases.types import QueryResult
from sqlalchemy import text as sql_text


def execute_sql(sql: str, db: DatabaseConnectionInfo) -> QueryResult:
    engine = db.to_sqlalchemy_engine()

    with engine.connect() as conn:
        result = conn.execute(sql_text(sql))

        if result.returns_rows:
            rows = result.fetchall()
            columns = list(result.keys())
        else:
            rows = []
            columns = []

        return {
            'columns': columns,
            'rows': [list(row) for row in rows],
        }
