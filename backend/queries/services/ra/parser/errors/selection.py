from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class SelectionSyntaxError(RASyntaxError):
    pass


@dataclass
class MissingSelectionConditionError(SelectionSyntaxError):
    @property
    def title(self) -> str:
        return 'Missing Selection Condition'

    @property
    def description(self) -> str:
        return 'A selection operation must include a condition to filter rows.'


@dataclass
class InvalidSelectionConditionError(SelectionSyntaxError):
    @property
    def description(self) -> str:
        return 'Invalid Selection Condition'
