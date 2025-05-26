from sqlglot.expressions import Subquery, Table

from ..scope import SelectScope
from ..types import SQLTable
from .errors import (
    DuplicateAliasError,
    MissingDerivedColumnAliasError,
    MissingDerivedTableAliasError,
    RelationNotFoundError,
)


class TableValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def validate(self, table: SQLTable) -> None:
        match table:
            case Table():
                return self._validate_table(table)

            case Subquery():
                return self._validate_derived_table(table)

    def _validate_table(self, table: Table) -> None:
        if table.name not in self.scope.db_schema:
            raise RelationNotFoundError(table)

    def _validate_derived_table(self, subquery: Subquery) -> None:
        from .query import validate_query

        # Derived tables must have an alias
        if not subquery.alias_or_name:
            raise MissingDerivedTableAliasError(subquery)

        # Validate the subquery
        subquery_scope = self.scope.tables.derived_table_scopes[subquery.alias_or_name]
        validate_query(subquery_scope)

        # Derived columns must have a unique alias
        aliases = []
        for expr in subquery_scope.projections.expressions:
            alias = expr.alias_or_name

            if not alias:
                raise MissingDerivedColumnAliasError(expr)

            if alias in aliases:
                raise DuplicateAliasError(expr)

            aliases.append(alias)
