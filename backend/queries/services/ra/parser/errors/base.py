from abc import ABC
from dataclasses import dataclass


@dataclass
class RASyntaxError(Exception, ABC):
    line: int
    column: int

    @property
    def title(self) -> str:
        return 'Syntax Error'

    @property
    def description(self) -> str | None:
        return None

    def __str__(self) -> str:
        return f'{self.title}:  {self.description}'


@dataclass
class MismatchedParenthesisError(RASyntaxError):
    @property
    def description(self) -> str:
        return 'Mismatched Parenthesis'


@dataclass
class MissingCommaError(RASyntaxError):
    @property
    def description(self) -> str:
        return 'Missing Comma in List'


@dataclass
class MissingOperandError(RASyntaxError):
    @property
    def description(self) -> str:
        return 'Missing Operand'


@dataclass
class InvalidOperatorError(RASyntaxError):
    @property
    def description(self) -> str:
        return 'Invalid Operator'
