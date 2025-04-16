from queries.types import ErrorPosition
from sqlglot import tokenize


def find_token_position(sql: str, target: str) -> ErrorPosition | None:
    for token in tokenize(sql):
        if token.text.lower() == target.lower():
            return to_error_position(token.line, token.col, len(token.text))
    return None


def to_error_position(line: int, col: int, length: int) -> ErrorPosition:
    return {
        'line': line,
        'start_col': col + 1 - length,
        'end_col': col + 1,
    }
