from enum import Enum
from typing import Any, TypedDict


class QueryExecutionResult(TypedDict):
    columns: list[str]
    rows: list[list[Any]]


class DataType(Enum):
    INTEGER = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    BOOLEAN = 'boolean'
    DATE = 'date'
    UNKNOWN = 'unknown'

    def __str__(self) -> str:
        return self.value


Schema = dict[str, dict[str, DataType]]
