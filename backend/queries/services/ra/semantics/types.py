from dataclasses import dataclass

from queries.services.types import ResultSchema
from ra_sql_visualisation.types import DataType


@dataclass
class TypedAttribute:
    name: str
    data_type: DataType


Output = tuple[ResultSchema, list[TypedAttribute]]
