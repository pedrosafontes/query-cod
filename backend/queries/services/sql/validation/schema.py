from databases.types import Schema
from queries.types import QueryError
from queries.utils.tokens import find_token_position
from sqlalchemy import Table
from sqlglot import expressions


def validate_schema(query_text: str, tree: expressions.Select, schema: Schema) -> list[QueryError]:
    errors: list[QueryError] = []

    # Validate table references
    referenced_tables = set()
    for table_expr in tree.find_all(expressions.Table):
        table_name = table_expr.name
        referenced_tables.add(table_name)
        if table_name not in schema.keys():
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

    return errors
