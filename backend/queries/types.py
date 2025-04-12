from typing import NotRequired, TypedDict

from databases.types import QueryExecutionResult


class ErrorPosition(TypedDict):
    line: int
    start_col: int
    end_col: int


class QueryError(TypedDict):
    message: str
    position: NotRequired[ErrorPosition | None]


class QueryValidationResult(TypedDict):
    valid: bool
    errors: NotRequired[list[QueryError]]


class QueryExecutionResponse(TypedDict):
    results: NotRequired[QueryExecutionResult]
    success: bool
