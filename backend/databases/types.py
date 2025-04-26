from typing import Any, TypedDict

from ra_sql_visualisation.types import DataType


class QueryExecutionResult(TypedDict):
    columns: list[str]
    rows: list[list[Any]]


TableName = str
ColumnName = str
TableSchema = dict[ColumnName, DataType]
Schema = dict[TableName, TableSchema]
