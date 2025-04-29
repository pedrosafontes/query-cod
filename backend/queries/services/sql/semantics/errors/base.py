from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlglot import Expression


@dataclass
class SQLSemanticError(Exception, ABC):
    source: Expression

    @abstractmethod
    def __str__(self) -> str:
        """Provide a human-readable error message."""
        pass
