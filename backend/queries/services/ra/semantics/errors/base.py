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

    @property
    def title(self) -> str:
        raise NotImplementedError('Subclasses must have a title')

    @property
    def description(self) -> str | None:
        return None

    def __str__(self) -> str:
        return f'{self.title}:  {self.description}'
