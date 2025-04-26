from ra_sql_visualisation.types import DataType


TableAlias = str
ColumnName = str
ProjectionSchema = dict[ColumnName, DataType]
ResultSchema = dict[TableAlias | None, ProjectionSchema]
