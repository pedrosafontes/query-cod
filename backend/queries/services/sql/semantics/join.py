from databases.types import Schema, TableSchema
from sqlglot.expressions import Identifier, Join, Subquery, Table

from .errors import (
    CrossJoinConditionError,
    DerivedColumnAliasRequiredError,
    DerivedTableMultipleSchemasError,
    MissingDerivedTableAliasError,
    MissingJoinConditionError,
    NoCommonColumnsError,
    UndefinedColumnError,
    UndefinedTableError,
)
from .expression import ExpressionValidator
from .scope import Scope
from .type_utils import assert_boolean, assert_comparable
from .types import ColumnTypes


class JoinValidator:
    def __init__(
        self,
        schema: Schema,
        scope: Scope,
        expr_validator: ExpressionValidator,
    ) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.expr_validator = expr_validator
        self.query_validator = QueryValidator(schema)

    def validate_join(self, join: Join) -> None:
        left_cols = self.scope.tables.snapshot_columns()
        self._add_table(join.this, self.scope)
        right_cols = self.schema[join.this.name]

        kind = join.method or join.args.get('kind', 'INNER')
        using = join.args.get('using')
        condition = join.args.get('on')

        if using:
            self._validate_using(using, left_cols, right_cols)
        elif kind == 'NATURAL':
            self._validate_natural_join(left_cols, right_cols)
        elif kind == 'CROSS':
            # CROSS JOINS must not have a condition
            if condition:
                raise CrossJoinConditionError()
        else:
            # INNER, LEFT, RIGHT, and FULL OUTER joins must have a condition
            if not condition:
                raise MissingJoinConditionError()
            assert_boolean(self.expr_validator.validate_basic(condition))

    def _validate_using(
        self, using: list[Identifier], left: ColumnTypes, right: TableSchema
    ) -> None:
        # All columns in USING must be present in both tables
        for ident in using:
            col = ident.name
            if col not in left:
                raise UndefinedColumnError(col)
            for ltype in left[col]:
                assert_comparable(ltype, right[col])

    def _validate_natural_join(self, left: ColumnTypes, right: TableSchema) -> None:
        shared = set(left) & set(right)
        # NATURAL JOIN must have at least one common column
        if not shared:
            raise NoCommonColumnsError()
        # All common columns must be comparable
        for col in shared:
            for ltype in left[col]:
                assert_comparable(ltype, right[col])

    def _add_table(self, table: Table | Subquery, scope: Scope) -> None:
        match table:
            case Table():
                name = table.name
                alias = table.alias_or_name
                table_schema = self.schema.get(name)
                if table_schema is None:
                    raise UndefinedTableError(name)
                scope.tables.add(alias, table_schema)

            case Subquery():
                alias = table.alias_or_name
                # Derived tables must have an alias
                if not alias:
                    raise MissingDerivedTableAliasError()
                sub_select = table.this
                for expr in sub_select.expressions:
                    # Derived columns must have an alias
                    if not expr.alias_or_name:
                        raise DerivedColumnAliasRequiredError(expr)
                try:
                    sub_schema = self.query_validator.validate(sub_select, scope).schema
                    [(_, columns)] = sub_schema.items()
                except ValueError:  # Unpack error
                    # Derived tables must return a single table
                    raise DerivedTableMultipleSchemasError() from None
                scope.tables.add(alias, columns)
