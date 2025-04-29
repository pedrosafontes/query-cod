from abc import ABC
from dataclasses import dataclass

from .base import SQLSemanticError


@dataclass
class QueryStructureError(SQLSemanticError, ABC):
    pass


@dataclass
class OrderByError(QueryStructureError, ABC):
    pass


@dataclass
class OrderByPositionError(OrderByError):
    order_by_pos: int
    max_position: int

    def __str__(self) -> str:
        return f'ORDER BY position {self.order_by_pos} is not in select list (valid positions: 1 to {self.max_position})'


@dataclass
class OrderByExpressionError(OrderByError):
    def __str__(self) -> str:
        return f'ORDER BY expression "{self.source}" must appear in the SELECT list'


@dataclass
class JoinError(QueryStructureError, ABC):
    pass


@dataclass
class MissingJoinConditionError(JoinError):
    def __str__(self) -> str:
        return 'JOIN requires an ON or USING clause'


@dataclass
class InvalidJoinConditionError(JoinError):
    def __str__(self) -> str:
        return 'CROSS JOIN does not support ON or USING clause'


@dataclass
class AliasError(QueryStructureError, ABC):
    pass


@dataclass
class MissingDerivedTableAliasError(AliasError):
    def __str__(self) -> str:
        return 'Every derived table must have its own alias'


@dataclass
class MissingDerivedColumnAliasError(AliasError):
    def __str__(self) -> str:
        return f'Derived column {self.source} must have an alias'


@dataclass
class DuplicateAliasError(AliasError):
    def __str__(self) -> str:
        return f"Duplicate alias '{self.source.alias_or_name}' in the query."


@dataclass
class AggregateError(QueryStructureError, ABC):
    pass


@dataclass
class AggregateInWhereError(AggregateError):
    def __str__(self) -> str:
        return 'Aggregate functions cannot be used in the WHERE clause'


@dataclass
class NestedAggregateError(AggregateError):
    def __str__(self) -> str:
        return 'Nested aggregate functions are not allowed'


@dataclass
class ColumnCountMismatchError(QueryStructureError):
    expected: int
    received: int

    def __str__(self) -> str:
        return f'Column count mismatch: expected {self.expected}, got {self.received}'


@dataclass
class UngroupedColumnError(QueryStructureError):
    columns: list[str]

    def __str__(self) -> str:
        if len(self.columns) == 1:
            return f'column "{self.columns[0]}" must appear in the GROUP BY clause or be used in an aggregate function'
        cols = '", "'.join(self.columns)
        return f'columns "{cols}" must appear in the GROUP BY clause or be used in an aggregate function'
