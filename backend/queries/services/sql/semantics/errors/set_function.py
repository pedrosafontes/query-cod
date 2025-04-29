from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class AggregateInWhereError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Aggregate functions cannot be used in the WHERE clause'


@dataclass
class NestedAggregateError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Nested aggregate functions are not allowed'
