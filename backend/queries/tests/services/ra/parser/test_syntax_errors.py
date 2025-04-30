import pytest
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors import (
    InvalidOperatorError,
    MismatchedParenthesisError,
    MissingOperandError,
)


@pytest.mark.parametrize(
    'query, expected_error',
    [
        ('R \\div', MissingOperandError),
        ('R && S', InvalidOperatorError),
        ('R + S', InvalidOperatorError),
        ('R || S', InvalidOperatorError),
        ('R * S', InvalidOperatorError),
        ('R ^^ S', InvalidOperatorError),
        ('R ! S', InvalidOperatorError),
        ('\\pi_{A} (R \\Join S', MismatchedParenthesisError),
        ('(R \\cup S', MismatchedParenthesisError),
        ('R \\cup S)', MismatchedParenthesisError),
        ('((R \\cap S)', MismatchedParenthesisError),
        ('R - (S', MismatchedParenthesisError),
    ],
)
def test_syntax_errors(query: str, expected_error: type) -> None:
    with pytest.raises(expected_error):
        parse_ra(query)
