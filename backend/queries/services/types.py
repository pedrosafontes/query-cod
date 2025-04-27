from databases.types import TableSchema
from ra_sql_visualisation.types import DataType


TableAlias = str
ProjectionSchema = TableSchema
ResultSchema = dict[TableAlias | None, ProjectionSchema]


def merge_common_column(result_schema: ResultSchema, col: str) -> None:
    types = []
    for schema in result_schema.values():
        if col in schema:
            types.append(schema.pop(col))
    result_schema[None][col] = DataType.dominant(types)
