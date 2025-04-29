from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class MissingJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return 'JOIN requires an ON or USING clause'


@dataclass
class CrossJoinConditionError(SQLSemanticError):
    def __str__(self) -> str:
        return 'CROSS JOIN does not support ON or USING clause'
