from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class TopNSyntaxError(RASyntaxError):
    pass


@dataclass
class InvalidTopNLimitError(TopNSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Top N Limit'


@dataclass
class InvalidTopNOrderByError(TopNSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Top N Order By'
