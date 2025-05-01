from abc import ABC
from dataclasses import dataclass

from queries.services.ra.parser.ast import ASTNode
from queries.types import ErrorPosition


@dataclass
class RASemanticError(Exception, ABC):
    source: ASTNode

    @property
    def position(self) -> ErrorPosition | None:
        return self.source.position

    @property
    def title(self) -> str:
        raise NotImplementedError('Subclasses must have a title')

    @property
    def description(self) -> str | None:
        return None

    def __str__(self) -> str:
        return f'{self.title}:  {self.description}'
