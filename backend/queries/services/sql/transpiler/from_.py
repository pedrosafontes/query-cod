from queries.services.ra.parser.ast import RAQuery
from sqlglot.expressions import From

from ..scope.query import SelectScope
from .table import TableTranspiler


class FromTranspiler:
    @staticmethod
    def transpile(scope: SelectScope) -> RAQuery:
        from_clause: From | None = scope.select.args.get('from')
        if not from_clause:
            raise ValueError('FROM clause is required in SELECT query')

        return TableTranspiler(scope).transpile(from_clause.this)
