from databases.types import Schema
from sqlglot.expressions import Subquery, Table

from ..errors import (
    DerivedColumnAliasRequiredError,
    DuplicateAliasError,
    MissingDerivedTableAliasError,
    UndefinedTableError,
)
from ..scope import Scope
from ..types import ProjectionSchema


class TableValidator:
    def __init__(self, schema: Schema, scope: Scope) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.query_validator = QueryValidator(schema)

    def validate(self, table: Table | Subquery) -> tuple[str, ProjectionSchema]:
        match table:
            case Table():
                return self._validate_table(table)

            case Subquery():
                return self._validate_derived_table(table)

    def _validate_table(self, table: Table) -> tuple[str, ProjectionSchema]:
        name = table.name
        alias = table.alias_or_name
        table_schema = self.schema.get(name)
        if table_schema is None:
            raise UndefinedTableError(name)
        return alias, table_schema

    def _validate_derived_table(self, subquery: Subquery) -> tuple[str, ProjectionSchema]:
        # Derived tables must have an alias
        alias = subquery.alias_or_name
        if not alias:
            raise MissingDerivedTableAliasError()

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

        return alias, self.query_validator.validate(query, self.scope).to_derived_table_schema()
