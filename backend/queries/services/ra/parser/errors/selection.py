from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class SelectionSyntaxError(RASyntaxError):
    pass


@dataclass
class MissingSelectionConditionError(SelectionSyntaxError):
    def __str__(self) -> str:
        return 'Missing Selection Condition'


@dataclass
class InvalidSelectionConditionError(SelectionSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Selection Condition'
