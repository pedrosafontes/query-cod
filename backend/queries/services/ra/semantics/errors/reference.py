from dataclasses import dataclass

from queries.services.ra.parser.ast import Attribute

from .base import RASemanticError


@dataclass
class RAReferenceError(RASemanticError):
    pass


@dataclass
class UndefinedRelationError(RAReferenceError):
    relation: str

    def _message(self) -> str:
        return f"Relation '{self.relation}' does not exist"


@dataclass
class UndefinedAttributeError(RAReferenceError):
    attribute: Attribute

    def _message(self) -> str:
        return f"Attribute '{self.attribute}' is not defined in the current context"


@dataclass
class AmbiguousAttributeError(RAReferenceError):
    attribute: str
    relations: list[str | None]

    def relation_names(self) -> list[str]:
        return [r or 'Unqualified' for r in self.relations]

    def _message(self) -> str:
        return f"Attribute '{self.attribute}' is ambiguous - it exists in multiple relations: {', '.join(self.relation_names())}"
