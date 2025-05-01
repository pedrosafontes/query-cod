from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class TopNSyntaxError(RASyntaxError):
    pass


@dataclass
class InvalidTopNLimitError(TopNSyntaxError):
    @property
    def title(self) -> str:
        return 'Invalid Top-N Limit'

    @property
    def description(self) -> str:
        return 'The Top-N operator requires a valid positive integer limit.'


@dataclass
class InvalidTopNOrderByError(TopNSyntaxError):
    @property
    def title(self) -> str:
        return 'Invalid Top-N Order By Attribute'

    @property
    def description(self) -> str:
        return 'A Top-N operator requires a valid attribute to sort by.'
