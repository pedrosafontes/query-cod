from abc import ABC
from dataclasses import dataclass

from sqlglot import Expression


@dataclass
class SQLSemanticError(Exception, ABC):
    source: Expression

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
        if self.description:
            return f'{self.title}:  {self.description}'
        else:
            return self.title
