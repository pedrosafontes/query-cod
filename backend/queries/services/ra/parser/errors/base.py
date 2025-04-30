from abc import ABC
from dataclasses import dataclass


@dataclass
class RASyntaxError(Exception, ABC):
    line: int
    column: int

    def __str__(self) -> str:
        return 'Syntax Error'


@dataclass
class MismatchedParenthesisError(RASyntaxError):
    def __str__(self) -> str:
        return 'Mismatched Parenthesis'


@dataclass
class MissingCommaError(RASyntaxError):
    def __str__(self) -> str:
        return 'Missing Comma in List'


@dataclass
class MissingOperandError(RASyntaxError):
    def __str__(self) -> str:
        return 'Missing Operand'


@dataclass
class InvalidOperatorError(RASyntaxError):
    def __str__(self) -> str:
        return 'Invalid Operator'
