from dataclasses import dataclass

from ra_sql_visualisation.types import DataType


@dataclass
class TypedAttribute:
    name: str
    data_type: DataType
    relations: set[str] | None = None
