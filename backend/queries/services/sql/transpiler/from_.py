from queries.services.ra.parser.ast import RAQuery

from ..scope.query import SelectScope
from .table import TableTranspiler


class FromTranspiler:
    @staticmethod
    def transpile(scope: SelectScope) -> RAQuery:
        if not scope.from_:
            raise ValueError('FROM clause is required in SELECT query')

        return TableTranspiler(scope).transpile(scope.from_.this)
