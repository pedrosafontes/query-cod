import sqlglot.expressions as exp
from databases.types import DataType, Schema

from .errors import (
    TypeMismatchError,
    UndefinedTableError,
)
from .types import Scope
from .utils import (
    is_date_format,
    is_time_format,
    is_timestamp_format,
)


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, expression: exp.Select) -> None:
        self._validate_query(expression, Scope())

    def _validate_query(self, expression: exp.Select, scope: Scope) -> None:
        self._validate_select(expression, scope)

    def _validate_select(self, select: exp.Select, outer_scope: Scope) -> None:
        scope = Scope(outer_scope)
        # 1. FROM clause - validate tables & populate scope
        self._populate_from_scope(select, scope)

        # 2. JOIN clause - validate joins & populate scope
        self._validate_joins(select, scope)

        # 3. Validate projections
        for proj in select.expressions:
            self._validate_expression(proj, scope)

        # 3. WHERE / HAVING boolean checks
        if where := select.args.get('where'):
            self._validate_expression(where.this, scope)

    def _populate_from_scope(self, select: exp.Select, scope: Scope) -> None:
        from_clause = select.args.get('from')
        if not isinstance(from_clause, exp.From):
            return

        self._validate_table_reference(from_clause.this, scope)

    def _validate_joins(self, select: exp.Select, scope: Scope) -> None:
        for join in select.args.get('joins', []):
            assert isinstance(join, exp.Join)  # noqa S101
            self._validate_table_reference(join.this, scope)

            # Validate JOIN condition
            if condition := join.args.get('on'):
                self._validate_expression(condition, scope)

    def _validate_table_reference(self, table_ref: exp.Table, scope: Scope) -> None:
        match table_ref:
            case exp.Table():
                table_name = table_ref.name
                alias = table_ref.alias_or_name
                schema_entry = self.schema.get(table_name)
                if schema_entry is None:
                    raise UndefinedTableError(table_name)
                for col, dtype in schema_entry.items():
                    scope.add(alias, col, dtype)

            case _:
                # TODO: Check for other table types
                pass

    def _validate_expression(  # type: ignore[return]
        self,
        node: exp.Expression,
        scope: Scope,
    ) -> DataType:
        match node:
            case exp.Literal():
                return self._infer_literal_type(node)

            case exp.Column():
                return scope.resolve(node.name)

            case exp.Binary():
                left_t = self._validate_expression(node.left, scope)
                right_t = self._validate_expression(node.right, scope)
                if not left_t.is_comparable_with(right_t):
                    raise TypeMismatchError(left_t, right_t)
                return DataType.BOOLEAN

            case exp.Not():
                if (not_t := self._validate_expression(node.this, scope)) != DataType.BOOLEAN:
                    raise TypeMismatchError(DataType.BOOLEAN, not_t)

                return DataType.BOOLEAN

            case _:
                # TODO: Handle other expressions
                pass

    def _infer_literal_type(self, node: exp.Literal) -> DataType:
        value = node.this

        if node.is_int:
            return DataType.INTEGER
        elif node.is_number:
            return DataType.FLOAT
        elif node.is_string:
            value = str(value).lower()
            if value in {'true', 'false'}:
                return DataType.BOOLEAN
            elif value in {'null', 'none'}:
                return DataType.NULL
            elif is_date_format(value):
                return DataType.DATE
            elif is_time_format(value):
                return DataType.TIME
            elif is_timestamp_format(value):
                return DataType.TIMESTAMP
            else:
                return DataType.VARCHAR
        else:
            raise ValueError(f'Unsupported literal: {node}')
