from abc import ABC
from dataclasses import dataclass

from queries.services.ra.parser.ast import ASTNode


@dataclass
class RASemanticError(Exception, ABC):
    source: ASTNode

    def __post_init__(self) -> None:
        if self.source.position:
            start_col, end_col = self.source.position
            self.start_col = start_col
            self.end_col = end_col

    def _message(self) -> str:
        raise NotImplementedError('Subclasses must implement _message()')

    def __str__(self) -> str:
        msg = self._message()
        if self.source.position:
            return f'{msg} (Columns {self.start_col}-{self.end_col})'
        return msg
