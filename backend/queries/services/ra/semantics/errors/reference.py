from dataclasses import dataclass

from queries.services.ra.ast import Attribute

from .base import RASemanticError


@dataclass
class RAReferenceError(RASemanticError):
    pass


@dataclass
class RelationNotFoundError(RAReferenceError):
    relation: str

    @property
    def title(self) -> str:
        return f"Relation '{self.relation}' does not exist"


@dataclass
class AttributeNotFoundError(RAReferenceError):
    attribute: Attribute

    @property
    def title(self) -> str:
        return f"Attribute '{self.attribute}' is not defined in the current context"

    @property
    def hint(self) -> str:
        return "Confirm that the attribute is defined in the input relation and that you're referencing it correctly."


@dataclass
class AmbiguousAttributeReferenceError(RAReferenceError):
    attribute: str
    relations: list[str | None]

    def relation_names(self) -> list[str]:
        return [r or 'Unqualified' for r in self.relations]

    @property
    def title(self) -> str:
        return f"Attribute '{self.attribute}' is ambiguous"

    def _description(self) -> str:
        return f"It exists in multiple relations: {', '.join(self.relation_names())}"

    @property
    def hint(self) -> str:
        return 'Qualify the attribute with its relation, e.g. `R.a` instead of just `a`.'
