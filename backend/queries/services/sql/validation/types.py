from typing import Any

from databases.types import Schema
from queries.types import QueryError
from queries.utils.tokens import find_token_position
from sqlalchemy import Boolean, Date, Integer, Numeric, String
from sqlglot import Expression, expressions


def validate_types(query_text: str, tree: expressions.Select, schema: Schema) -> list[QueryError]:
    errors: list[QueryError] = []

    for binary_expr in tree.find_all(expressions.Condition):
        left = binary_expr.args.get('this')
        right = binary_expr.args.get('expression')
        if not left or not right:
            continue

        left_type = _infer_expr_type(left, schema)
        right_type = _infer_expr_type(right, schema)

        if (
            left_type != 'unknown'
            and right_type != 'unknown'
            and not _are_types_compatible(left_type, right_type)
        ):
            errors.append(
                {
                    'message': f'Type mismatch: cannot compare {left_type} with {right_type}',
                    'position': find_token_position(query_text, str(binary_expr)),
                }
            )

    return errors


def _infer_expr_type(expr: Expression, schema: Schema) -> str:
    if isinstance(expr, expressions.Literal):
        if expr.is_string:
            return 'str'
        if expr.is_number:
            try:
                value = float(expr.this)
                return 'int' if value.is_integer() else 'float'
            except ValueError:
                return 'unknown'

    elif isinstance(expr, expressions.Column):
        table_expr = expr.args.get('table')
        table_name = table_expr.name if table_expr else None
        col_name = expr.name

        if table_name and table_name in schema and col_name in schema[table_name]:
            return _resolve_type(schema[table_name][col_name])
        else:
            for table_schema in schema.values():
                if col_name in table_schema:
                    return _resolve_type(table_schema[col_name])

    elif isinstance(expr, expressions.Anonymous):
        func_name = expr.name.lower()
        if func_name in {'count', 'rank', 'row_number'}:
            return 'int'
        elif func_name in {'sum', 'avg', 'max', 'min'}:
            return 'float'

    return 'unknown'


def _resolve_type(sqlatype: Any) -> str:
    if isinstance(sqlatype, Integer):
        return 'int'
    if isinstance(sqlatype, Numeric):
        return 'float'
    if isinstance(sqlatype, String):
        return 'str'
    if isinstance(sqlatype, Boolean):
        return 'bool'
    if isinstance(sqlatype, Date):
        return 'date'
    return 'unknown'


def _are_types_compatible(left: str, right: str) -> bool:
    numeric_types = {'int', 'float'}
    if left in numeric_types and right in numeric_types:
        return True
    return left == right
