from databases.types import TableSchema
from ra_sql_visualisation.types import DataType


RelationName = str
AttributeSchema = TableSchema
RelationalSchema = dict[RelationName | None, AttributeSchema]


def merge_common_column(result_schema: RelationalSchema, col: str) -> None:
    types = []
    for schema in result_schema.values():
        if col in schema:
            types.append(schema.pop(col))
    result_schema[None][col] = DataType.dominant(types)
