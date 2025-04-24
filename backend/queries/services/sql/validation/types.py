from databases.types import DataType


TableAlias = str
ColumnName = str
ProjectionSchema = dict[ColumnName, DataType]
ResultSchema = dict[TableAlias | None, ProjectionSchema]
ColumnTypes = dict[ColumnName, list[DataType]]
