from queries.services.ra.parser.ast import RAQuery
from queries.services.sql.scope.query import SelectScope
from sqlglot.expressions import From

from .table import TableTranspiler


class FromTranspiler:
    @staticmethod
    def transpile(scope: SelectScope) -> RAQuery:
        from_clause: From | None = scope.select.args.get('from')
        if not from_clause:
            raise ValueError('FROM clause is required in SELECT query')

        return TableTranspiler(scope).transpile(from_clause.this)
