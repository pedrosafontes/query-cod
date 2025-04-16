from dataclasses import dataclass
from typing import cast

from databases.types import DataType, Schema
from queries.types import QueryError
from queries.utils.tokens import find_token_position
from sqlglot import Expression, expressions


@dataclass
class TypeInfo:
    data_type: DataType
    source: str | None = None  # e.g. table.column, literal, function


def validate_types(query_text: str, tree: expressions.Select, schema: Schema) -> list[QueryError]:
    errors: list[QueryError] = []

    # Validate all conditions including WHERE, JOIN, and HAVING clauses
    for binary_expr in tree.find_all(expressions.Condition):
        left = binary_expr.args.get('this')
        right = binary_expr.args.get('expression')
        operator = binary_expr.args.get('op')

        if not left or not right:
            continue

        left_type_info = infer_expr_type(left, schema)
        right_type_info = infer_expr_type(right, schema)

        if (
            left_type_info.data_type == DataType.UNKNOWN
            or right_type_info.data_type == DataType.UNKNOWN
        ):
            continue

        if not are_types_compatible(left_type_info.data_type, right_type_info.data_type, operator):
            errors.append(
                {
                    'message': generate_type_mismatch_message(
                        left_type_info, right_type_info, str(operator)
                    ),
                    'position': find_token_position(query_text, str(binary_expr)),
                }
            )

    # TODO: Add validation for GROUP BY, ORDER BY, etc.

    return errors


def infer_expr_type(expr: Expression, schema: Schema) -> TypeInfo:
    if isinstance(expr, expressions.Literal):
        return infer_literal_type(expr)

    elif isinstance(expr, expressions.Column):
        return infer_column_type(expr, schema)

    elif isinstance(expr, expressions.Anonymous):
        return infer_function_type(expr)

    elif isinstance(expr, expressions.Binary):
        return infer_binary_operation_type(expr, schema)

    return TypeInfo(DataType.UNKNOWN)


def infer_literal_type(expr: expressions.Literal) -> TypeInfo:
    if expr.is_string:
        return TypeInfo(DataType.STRING, f"literal '{expr.this}'")

    if expr.is_number:
        try:
            value = float(expr.this)
            if value.is_integer():
                return TypeInfo(DataType.INTEGER, f'literal {expr.this}')
            return TypeInfo(DataType.FLOAT, f'literal {expr.this}')
        except ValueError:
            pass

    if str(expr.this).lower() in ('true', 'false'):
        return TypeInfo(DataType.BOOLEAN, f'literal {expr.this}')

    return TypeInfo(DataType.UNKNOWN)


def infer_column_type(expr: expressions.Column, schema: Schema) -> TypeInfo:
    table_expr = expr.args.get('table')
    table_name = table_expr.name if table_expr else None
    col_name = expr.name
    source = f'{table_name}.{col_name}' if table_name else col_name

    if table_name and table_name in schema and col_name in schema[table_name]:
        return TypeInfo(schema[table_name][col_name], source)

    if not table_name:
        for table, columns in schema.items():
            if col_name in columns:
                return TypeInfo(columns[col_name], f'{table}.{col_name}')

    return TypeInfo(DataType.UNKNOWN, source)


def infer_function_type(expr: expressions.Anonymous) -> TypeInfo:
    func_name = expr.name.lower()
    source = f'{func_name}()'

    if func_name in {'count', 'rank', 'row_number', 'dense_rank'}:
        return TypeInfo(DataType.INTEGER, source)

    if func_name in {'sum', 'avg', 'max', 'min'}:
        return TypeInfo(DataType.FLOAT, source)

    if func_name in {'concat', 'substring', 'trim', 'upper', 'lower'}:
        return TypeInfo(DataType.STRING, source)

    if func_name in {'current_date', 'current_timestamp'}:
        return TypeInfo(DataType.DATE, source)

    if func_name in {'exists'}:
        return TypeInfo(DataType.BOOLEAN, source)

    return TypeInfo(DataType.UNKNOWN, source)


def infer_binary_operation_type(expr: expressions.Binary, schema: Schema) -> TypeInfo:
    left_type = infer_expr_type(cast(Expression, expr.args.get('this')), schema)
    right_type = infer_expr_type(cast(Expression, expr.args.get('expression')), schema)
    operator = expr.args.get('op')

    if operator in ('=', '!=', '<>', '>', '<', '>=', '<='):
        return TypeInfo(DataType.BOOLEAN, 'comparison result')

    if operator in ('+', '-', '*', '/', '%'):
        if left_type.data_type in (DataType.INTEGER, DataType.FLOAT) and right_type.data_type in (
            DataType.INTEGER,
            DataType.FLOAT,
        ):
            # Float has precedence over integer
            if DataType.FLOAT in (left_type.data_type, right_type.data_type):
                return TypeInfo(DataType.FLOAT, 'arithmetic result')
            return TypeInfo(DataType.INTEGER, 'arithmetic result')

    if operator == '||' or (
        operator == '+'
        and left_type.data_type == DataType.STRING
        and right_type.data_type == DataType.STRING
    ):
        return TypeInfo(DataType.STRING, 'string concatenation')

    return TypeInfo(DataType.UNKNOWN)


def are_types_compatible(left: DataType, right: DataType, operator: str | None = None) -> bool:
    if left == right:
        return True

    # Numeric types are compatible with each other
    numeric_types = {DataType.INTEGER, DataType.FLOAT}
    if left in numeric_types and right in numeric_types:
        return True

    # String comparisons with dates
    if operator in ('=', '!=', '<>', '>', '<', '>=', '<='):
        if (left == DataType.STRING and right == DataType.DATE) or (
            left == DataType.DATE and right == DataType.STRING
        ):
            return True

    return False


def generate_type_mismatch_message(left_type: TypeInfo, right_type: TypeInfo, operator: str) -> str:
    """Create a user-friendly error message for type mismatch"""
    op_description = {
        '=': 'compare',
        '!=': 'compare',
        '<>': 'compare',
        '>': 'compare',
        '<': 'compare',
        '>=': 'compare',
        '<=': 'compare',
        '+': 'add',
        '-': 'subtract',
        '*': 'multiply',
        '/': 'divide',
        '%': 'calculate modulo of',
    }.get(operator, 'operate on')

    left_desc = (
        f'{left_type.data_type} ({left_type.source})'
        if left_type.source
        else str(left_type.data_type)
    )
    right_desc = (
        f'{right_type.data_type} ({right_type.source})'
        if right_type.source
        else str(right_type.data_type)
    )

    return f'Type mismatch: Cannot {op_description} {left_desc} with {right_desc}'
