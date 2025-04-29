from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class OrderByPositionError(SQLSemanticError):
    order_by_pos: int
    max_position: int

    def __str__(self) -> str:
        return f'ORDER BY position {self.order_by_pos} is not in select list (valid positions: 1 to {self.max_position})'


@dataclass
class OrderByExpressionError(SQLSemanticError):
    def __str__(self) -> str:
        return f'ORDER BY expression "{self.source}" must appear in the SELECT list'
