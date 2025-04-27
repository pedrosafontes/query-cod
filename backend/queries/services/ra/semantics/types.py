from dataclasses import dataclass

from queries.services.types import RelationalSchema
from ra_sql_visualisation.types import DataType


@dataclass
class TypedAttribute:
    name: str
    data_type: DataType


@dataclass
class RelationOutput:
    schema: RelationalSchema
    attrs: list[TypedAttribute]
