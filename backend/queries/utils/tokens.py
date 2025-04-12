from queries.types import ErrorPosition
from sqlglot import tokenize


def find_token_position(sql: str, target: str) -> ErrorPosition | None:
    print(f"Finding position of token '{target}' in SQL: {sql}")
    for token in tokenize(sql):
        print(f'Checking token: {token.text} at line {token.line}, col {token.col}')
        if token.text.lower() == target.lower():
            print(f"Found token '{target}' at line {token.line}, col {token.col}")
            return to_error_position(token.line, token.col, len(token.text))
    return None


def to_error_position(line: int, col: int, length: int) -> ErrorPosition:
    return {
        'line': line,
        'start_col': col + 1 - length,
        'end_col': col + 1,
    }
