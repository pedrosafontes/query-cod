from databases.types import ColumnSchema
from ra_sql_visualisation.types import DataType


RelationName = str
AttributeSchema = ColumnSchema
RelationalSchema = dict[RelationName | None, AttributeSchema]


def merge_common_column(result_schema: RelationalSchema, col: str) -> None:
    types = []
    for schema in result_schema.values():
        if col in schema:
            types.append(schema.pop(col))
    result_schema[None][col] = DataType.dominant(types)


def flatten(schema: RelationalSchema) -> AttributeSchema:
    flat: AttributeSchema = {}
    for attributes in schema.values():
        for attr, t in attributes.items():
            flat[attr] = t
    return flat
