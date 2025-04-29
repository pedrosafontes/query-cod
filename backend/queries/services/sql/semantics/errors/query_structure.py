from abc import ABC
from dataclasses import dataclass
from typing import cast, get_args

from sqlglot.expressions import Select

from ..types import AggregateFunction
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
        return f'ORDER BY position {self.order_by_pos} is invalid; must be between 1 and {self.max_position}.'


@dataclass
class OrderByExpressionError(OrderByError):
    def __str__(self) -> str:
        return f'ORDER BY expression "{self.source}" must be present in the SELECT list.'


@dataclass
class JoinError(QueryStructureError, ABC):
    pass


@dataclass
class MissingJoinConditionError(JoinError):
    def __str__(self) -> str:
        return 'JOIN operation requires an ON or USING clause.'


@dataclass
class InvalidJoinConditionError(JoinError):
    def __str__(self) -> str:
        return 'CROSS JOIN must not specify ON or USING clauses.'


@dataclass
class AliasError(QueryStructureError, ABC):
    pass


@dataclass
class MissingDerivedTableAliasError(AliasError):
    def __str__(self) -> str:
        return f'Derived column "{self.source}" must have an explicit alias.'


@dataclass
class MissingDerivedColumnAliasError(AliasError):
    def __str__(self) -> str:
        return f'Derived column "{self.source}" must have an alias.'


@dataclass
class DuplicateAliasError(AliasError):
    def __str__(self) -> str:
        return f"Duplicate alias detected: '{self.source.alias_or_name}'. Aliases must be unique within a query."


@dataclass
class AggregateError(QueryStructureError, ABC):
    pass


@dataclass
class AggregateInWhereError(AggregateError):
    def __str__(self) -> str:
        where = cast(Select, self.source.find_ancestor(Select)).args['where']
        return f'Aggregate functions are not permitted in the WHERE clause: {where}.'


@dataclass
class NestedAggregateError(AggregateError):
    def __str__(self) -> str:
        outer = self.source.find_ancestor(*get_args(AggregateFunction))
        return f'Nested aggregate functions are not permitted: {outer}'


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
            start = f'Column "{self.columns[0]}"'
        else:
            start = f'Columns {', '.join(self.columns)}'
        return f'{start} must appear in the GROUP BY clause or be used in an aggregate function'
