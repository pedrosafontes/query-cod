from typing import TypedDict

from databases.types import QueryResult


class Feedback(TypedDict):
    correct: bool
    results: QueryResult | None
