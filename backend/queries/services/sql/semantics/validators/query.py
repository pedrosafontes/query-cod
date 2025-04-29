from databases.types import Schema
from sqlglot import Expression
from sqlglot.expressions import (
    Select,
)

from ..scope import Scope
from ..scope.projections import ProjectionsScope
from ..types import SetOperation
from .select import SelectValidator
from .set_operation import SetOperationValidator


class QueryValidator:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, query: Expression, outer_scope: Scope | None) -> ProjectionsScope:
        scope = Scope(outer_scope)
        match query:
            case Select():
                SelectValidator(self.schema, scope).validate(query)
            case query if isinstance(query, SetOperation):
                SetOperationValidator(self.schema, scope).validate(query)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')
        return scope.projections
