from dataclasses import dataclass

from queries.services.ra.ast import Attribute
from queries.services.types import RelationalSchema, RelationName
from ra_sql_visualisation.types import DataType


@dataclass
class TypedAttribute:
    name: str
    data_type: DataType


Match = tuple[RelationName | None, DataType]


@dataclass
class RelationOutput:
    schema: RelationalSchema
    attrs: list[TypedAttribute]

    def resolve(self, attr: Attribute) -> list[Match]:
        if attr.relation:
            return self._resolve_qualified(attr)
        else:
            return self._resolve_unqualified(attr)

    def _resolve_qualified(self, attr: Attribute) -> list[Match]:
        t = self.schema.get(attr.relation, {}).get(attr.name)
        if t is None:
            return []
        return [(attr.relation, t)]

    def _resolve_unqualified(self, attr: Attribute) -> list[Match]:
        return [
            (relation, attrs[attr.name])
            for relation, attrs in self.schema.items()
            if attr.name in attrs
        ]
