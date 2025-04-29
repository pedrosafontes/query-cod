from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class DuplicateAliasError(SQLSemanticError):
    def __str__(self) -> str:
        return f"Duplicate alias '{self.source.alias_or_name}' in the query."
