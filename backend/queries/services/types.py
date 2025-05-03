from databases.types import Columns, Schema
from ra_sql_visualisation.types import DataType


RelationName = str
AttributeName = str
Attributes = dict[AttributeName, DataType]
RelationalSchema = dict[RelationName | None, Attributes]


def merge_common_column(result_schema: RelationalSchema, col: str) -> None:
    types = []
    for schema in result_schema.values():
        if col in schema:
            types.append(schema.pop(col))
    result_schema.setdefault(None, {})[col] = DataType.dominant(types)


def flatten(schema: RelationalSchema) -> Attributes:
    flat: Attributes = {}
    for attributes in schema.values():
        for attr, t in attributes.items():
            flat[attr] = t
    return flat


def to_relational_schema(schema: Schema) -> RelationalSchema:
    return {name: _columns_to_attributes(columns) for name, columns in schema.items()}


def _columns_to_attributes(columns: Columns) -> Attributes:
    return {name: col['type'] for name, col in columns.items()}
