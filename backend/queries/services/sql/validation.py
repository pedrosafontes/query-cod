from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql
from queries.types import QueryError, QueryValidationResult
from queries.utils.tokens import find_token_position, to_error_position
from sqlalchemy import Table, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlglot import ParseError, expressions, parse_one


def validate_sql(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    if not query_text.strip():
        return {'valid': False}

    tree, syntax_errors = _validate_sql_syntax(query_text, db)
    if syntax_errors:
        return {'valid': False, 'errors': syntax_errors}

    assert tree  # noqa: S101
    schema_result = _validate_sql_schema(query_text, tree, db)
    if schema_result['errors']:
        return schema_result

    explain_result = _validate_sql_explain(query_text, db)
    if explain_result is not None:
        return explain_result

    return {'valid': True}


def _validate_sql_syntax(
    query_text: str, db: DatabaseConnectionInfo
) -> tuple[expressions.Select | None, list[QueryError]]:
    try:
        tree = parse_one(
            query_text,
            read=_database_type_to_sqlglot(db.database_type),
            into=expressions.Select,
        )
        return tree, []
    except ParseError as e:
        return None, [
            {
                'message': err['description'],
                'position': to_error_position(err['line'], err['col'], len(err['highlight'])),
            }
            for err in e.errors
        ]


def _validate_sql_schema(
    query_text: str, tree: expressions.Select, db: DatabaseConnectionInfo
) -> QueryValidationResult:
    try:
        engine = db.to_sqlalchemy_engine()
        inspector = inspect(engine)
        db_tables = inspector.get_table_names()
        schema = {
            table: [col['name'] for col in inspector.get_columns(table)] for table in db_tables
        }
    except SQLAlchemyError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'message': f'Error inspecting database schema: {e.__class__.__name__}: {e}',
                }
            ],
        }

    errors: list[QueryError] = []

    # Validate table references
    referenced_tables = set()
    for table_expr in tree.find_all(expressions.Table):
        table_name = table_expr.name
        referenced_tables.add(table_name)
        if table_name not in db_tables:
            errors.append(
                {
                    'message': f'Unknown table "{table_name}"',
                    'position': find_token_position(query_text, table_name),
                }
            )

    # Find aliases (AS ...)
    aliased_names = {alias.alias for alias in tree.find_all(expressions.Alias) if alias.alias}

    # Validate column references
    for col_expr in tree.find_all(expressions.Column):
        col_name = col_expr.name
        col_table_expr: Table | None = col_expr.args.get('table')
        col_table_name: str | None = col_table_expr.name if col_table_expr else None

        # Skip if it's an alias
        if col_name in aliased_names:
            continue

        # Qualified column
        if col_table_name:
            if col_table_name not in schema:
                continue  # Already reported unknown table
            if col_name not in schema[col_table_name]:
                errors.append(
                    {
                        'message': f'Unknown column "{col_name}" in table "{col_table_name}"',
                        'position': find_token_position(query_text, col_name),
                    }
                )
        else:
            # Unqualified column: check if it exists in any referenced table
            found = any(col_name in schema.get(tbl, set()) for tbl in referenced_tables)
            if not found:
                errors.append(
                    {
                        'message': f'Unknown column "{col_name}"',
                        'position': find_token_position(query_text, col_name),
                    }
                )

    return {'valid': not errors, 'errors': errors}


def _validate_sql_explain(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    try:
        execute_sql(f'EXPLAIN {query_text}', db)
    except SQLAlchemyError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'message': f'{e.__class__.__name__}: {e}',
                }
            ],
        }
    return {'valid': True}


def _database_type_to_sqlglot(db_type: str) -> str:
    return {
        'postgresql': 'postgres',
    }.get(db_type, db_type)
