from dataclasses import dataclass

from databases.types import DataType


@dataclass
class TypedAttribute:
    name: str
    data_type: DataType
    relations: set[str] | None = None
