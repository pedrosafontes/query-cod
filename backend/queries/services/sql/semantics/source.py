from databases.types import Schema
from sqlglot.expressions import Subquery, Table

from .errors import (
    DerivedColumnAliasRequiredError,
    DerivedTableMultipleSchemasError,
    MissingDerivedTableAliasError,
    UndefinedTableError,
)
from .scope import Scope


class SourceValidator:
    def __init__(self, schema: Schema, scope: Scope) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.query_validator = QueryValidator(schema)

    def validate(self, table: Table | Subquery) -> None:
        match table:
            case Table():
                name = table.name
                alias = table.alias_or_name
                table_schema = self.schema.get(name)
                if table_schema is None:
                    raise UndefinedTableError(name)
                self.scope.sources.add(alias, table_schema)

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
                    sub_schema = self.query_validator.validate(sub_select, self.scope).schema
                    [(_, columns)] = sub_schema.items()
                except ValueError:  # Unpack error
                    # Derived tables must return a single table
                    raise DerivedTableMultipleSchemasError() from None
                self.scope.sources.add(alias, columns)
