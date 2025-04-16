from typing import Any, TypedDict


class QueryExecutionResult(TypedDict):
    columns: list[str]
    rows: list[list[Any]]


Schema = dict[str, dict[str, Any]]
