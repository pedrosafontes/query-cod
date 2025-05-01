from dataclasses import dataclass

from .base import RASyntaxError


@dataclass
class JoinSyntaxError(RASyntaxError):
    pass


@dataclass
class InvalidThetaJoinConditionError(JoinSyntaxError):
    @property
    def description(self) -> str:
        return 'Invalid Theta Join Condition'


@dataclass
class MissingThetaJoinConditionError(JoinSyntaxError):
    @property
    def title(self) -> str:
        return 'Missing Theta Join Condition'

    @property
    def description(self) -> str:
        return 'A theta join must include a join condition.'
