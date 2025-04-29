from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class UndefinedTableError(SQLSemanticError):
    name: str | None = None

    def __str__(self) -> str:
        return f"Table '{self.name or self.source.name}' does not exist"
