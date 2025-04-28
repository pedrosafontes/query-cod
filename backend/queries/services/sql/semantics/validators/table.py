from databases.types import Schema
from queries.services.types import AttributeSchema, flatten
from sqlglot.expressions import Subquery, Table

from ..errors import (
    DerivedColumnAliasRequiredError,
    DuplicateAliasError,
    MissingDerivedTableAliasError,
    UndefinedTableError,
)
from ..scope import Scope


class TableValidator:
    def __init__(self, schema: Schema, scope: Scope) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.query_validator = QueryValidator(schema)

    def validate(self, table: Table | Subquery) -> AttributeSchema:
        match table:
            case Table():
                return self._validate_table(table)

            case Subquery():
                return self._validate_derived_table(table)

    def _validate_table(self, table: Table) -> AttributeSchema:
        name = table.name
        table_schema = self.schema.get(name)
        if table_schema is None:
            raise UndefinedTableError(table)
        return table_schema

    def _validate_derived_table(self, subquery: Subquery) -> AttributeSchema:
        # Derived tables must have an alias
        if not subquery.alias_or_name:
            raise MissingDerivedTableAliasError(subquery)

        # Derived columns must have a unique alias
        query = subquery.this
        col_aliases = []
        for expr in query.expressions:
            col_alias = expr.alias_or_name

            if not col_alias:
                raise DerivedColumnAliasRequiredError(expr)

            if col_alias in col_aliases:
                raise DuplicateAliasError(expr)

            col_aliases.append(col_alias)

        return flatten(self.query_validator.validate(query, self.scope).schema)
