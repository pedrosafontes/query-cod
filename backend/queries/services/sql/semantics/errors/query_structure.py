from abc import ABC
from dataclasses import dataclass
from typing import cast

from queries.services.sql.types import aggregate_functions
from sqlglot.expressions import Expression, Select

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

    @property
    def title(self) -> str:
        return f'ORDER BY position {self.order_by_pos} is invalid'

    @property
    def description(self) -> str:
        return f'Must be between 1 and {self.max_position}.'


@dataclass
class JoinError(QueryStructureError, ABC):
    pass


@dataclass
class MissingJoinConditionError(JoinError):
    @property
    def title(self) -> str:
        return 'JOIN operation requires an ON or USING clause.'


@dataclass
class InvalidJoinConditionError(JoinError):
    @property
    def title(self) -> str:
        return 'CROSS JOIN must not specify ON or USING clauses.'


@dataclass
class AliasError(QueryStructureError, ABC):
    pass


@dataclass
class MissingDerivedTableAliasError(AliasError):
    @property
    def title(self) -> str:
        return 'Missing derived table alias'

    @property
    def description(self) -> str:
        return f'Derived table `{self.source}` must have an explicit alias.'

    @property
    def hint(self) -> str:
        return (
            'Use `SELECT ... FROM (subquery)` **`AS alias`** to give a name to the subquery result.'
        )


@dataclass
class MissingDerivedColumnAliasError(AliasError):
    @property
    def title(self) -> str:
        return 'Missing derived column alias'

    @property
    def description(self) -> str:
        return f'Derived column `{self.source}` must have an alias.'

    @property
    def hint(self) -> str:
        return 'Use `SELECT expression` **`AS alias`** to name derived columns.'


@dataclass
class DuplicateAliasError(AliasError):
    @property
    def title(self) -> str:
        return 'Duplicate alias'

    @property
    def description(self) -> str:
        return f'Duplicate alias detected: `{self.source.alias_or_name}`. Aliases must be unique within a query.'

    @property
    def hint(self) -> str:
        return 'Ensure each alias is used only once per `SELECT` or `FROM` clause.'


@dataclass
class AggregateError(QueryStructureError, ABC):
    pass


@dataclass
class AggregateInWhereError(AggregateError):
    @property
    def title(self) -> str:
        return 'Aggregate functions are not permitted in the WHERE clause'

    @property
    def description(self) -> str:
        where: Select = cast(Select, self.source.find_ancestor(Select)).args['where']
        return f'In: `{where.sql()}`'

    @property
    def hint(self) -> str:
        return 'Move the aggregate expression to the `HAVING` clause instead.'


@dataclass
class NestedAggregateError(AggregateError):
    @property
    def title(self) -> str:
        return 'Nested aggregate functions are not permitted'

    @property
    def description(self) -> str | None:
        outer: Expression | None = self.source.find_ancestor(*aggregate_functions)
        return f'In: `{outer.sql()}`' if outer else None


@dataclass
class ColumnCountMismatchError(QueryStructureError):
    expected: int
    received: int

    @property
    def title(self) -> str:
        return 'Column count mismatch'

    @property
    def description(self) -> str:
        return f'Expected {self.expected}, got {self.received}. In: `{self.source.sql()}`'


@dataclass
class UngroupedColumnError(QueryStructureError):
    columns: list[str]

    def _single_column(self) -> bool:
        return len(self.columns) == 1

    @property
    def title(self) -> str:
        return f'Invalid column reference{'' if self._single_column() else 's'}'

    @property
    def description(self) -> str:
        if self._single_column():
            start = f'Column `{self.columns[0]}`'
        else:
            start = f'Columns {', '.join(self.columns)}'
        return f'{start} must appear in the GROUP BY clause or be used in an aggregate function'

    @property
    def hint(self) -> str:
        return 'Add the column(s) to the `GROUP BY` clause or wrap them in an aggregate function like `MAX()` or `SUM()`.'
