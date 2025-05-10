from typing import Any, TypedDict

from ra_sql_visualisation.types import DataType


class QueryResult(TypedDict):
    columns: list[str]
    rows: list[list[Any]]


TableName = str
ColumnName = str


class ForeignKey(TypedDict):
    table: TableName
    column: ColumnName


class Column(TypedDict):
    type: DataType
    nullable: bool
    primary_key: bool
    references: ForeignKey | None


Columns = dict[ColumnName, Column]

Schema = dict[TableName, Columns]
