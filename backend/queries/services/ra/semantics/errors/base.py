from abc import ABC
from dataclasses import dataclass

from queries.services.ra.ast import ASTNode


@dataclass
class RASemanticError(Exception, ABC):
    source: ASTNode

    @property
    def title(self) -> str:
        raise NotImplementedError('Subclasses must have a title')

    @property
    def description(self) -> str | None:
        return None

    @property
    def hint(self) -> str | None:
        return None

    def __str__(self) -> str:
        return f'{self.title}:  {self.description}'
