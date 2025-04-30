from sqlglot import ErrorLevel, expressions, parse_one


def parse_sql(query_text: str) -> expressions.Select:
    return parse_one(query_text, into=expressions.Select, error_level=ErrorLevel.RAISE)


def _database_type_to_sqlglot(db_type: str) -> str:
    return {
        'postgresql': 'postgres',
    }.get(db_type, db_type)
