from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class JoinSyntaxError(RASyntaxError):
    pass


@dataclass
class InvalidThetaJoinConditionError(JoinSyntaxError):
    def __str__(self) -> str:
        return 'Invalid Theta Join Condition'


@dataclass
class MissingThetaJoinConditionError(JoinSyntaxError):
    def __str__(self) -> str:
        return 'Missing Theta Join Condition'
