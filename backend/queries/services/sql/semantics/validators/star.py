from queries.services.types import RelationalSchema
from sqlglot.expressions import Column, Expression, Identifier

from ..errors.query_structure import UngroupedColumnError
from ..scope import Scope


class StarValidator:
    def __init__(self, scope: Scope) -> None:
        self.scope = scope

    def validate(self, expr: Expression) -> RelationalSchema:
        table_ident: Identifier | None = expr.args.get('table')

        schema = (
            self.scope.tables.get_table_schema(table_ident.this, expr)
            if table_ident
            else self.scope.tables.get_schema()
        )

        if self.scope.is_grouped:
            missing: list[str] = []
            for table, table_schema in schema.items():
                for col, _ in table_schema.items():
                    col_expr = Column(this=col, table=table)
                    if not self.scope.group_by.contains(col_expr):
                        missing.append(col)

            if missing:
                raise UngroupedColumnError(expr, missing)

        return schema
