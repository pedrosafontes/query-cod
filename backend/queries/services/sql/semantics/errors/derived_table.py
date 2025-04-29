from dataclasses import dataclass

from . import SQLSemanticError


@dataclass
class MissingDerivedTableAliasError(SQLSemanticError):
    def __str__(self) -> str:
        return 'Every derived table must have its own alias'


@dataclass
class DerivedColumnAliasRequiredError(SQLSemanticError):
    def __str__(self) -> str:
        return f'Derived column {self.source} must have an alias'
