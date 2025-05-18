from queries.services.types import Attributes, RelationalSchema
from sqlglot.expressions import Subquery, Table

from ..errors import (
    DuplicateAliasError,
    MissingDerivedColumnAliasError,
    MissingDerivedTableAliasError,
    RelationNotFoundError,
)
from ..inference import TypeInferrer
from ..scope import Scope


class TableValidator:
    def __init__(self, schema: RelationalSchema, scope: Scope) -> None:
        from .query import QueryValidator

        self.schema = schema
        self.scope = scope
        self.query_validator = QueryValidator(schema)
        self._type_inferrer = TypeInferrer(scope)

    def validate(self, table: Table | Subquery) -> Attributes:
        match table:
            case Table():
                return self._validate_table(table)

            case Subquery():
                return self._validate_derived_table(table)

    def _validate_table(self, table: Table) -> Attributes:
        name = table.name
        columns = self.schema.get(name)
        if columns is None:
            raise RelationNotFoundError(table)
        return columns

    def _validate_derived_table(self, subquery: Subquery) -> Attributes:
        # Derived tables must have an alias
        if not subquery.alias_or_name:
            raise MissingDerivedTableAliasError(subquery)

        # Derived columns must have a unique alias
        query = subquery.this
        cols = {}
        for expr in query.expressions:
            alias = expr.alias_or_name

            if not alias:
                raise MissingDerivedColumnAliasError(expr)

            if alias in cols:
                raise DuplicateAliasError(expr)

            cols[alias] = self._type_inferrer.infer(expr)

        return cols
