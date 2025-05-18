from queries.services.sql.semantics.scope import Scope
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Alias, Column, Expression
from sqlglot.expressions import DataType as SQLGlotDataType

from .errors.object_reference import ColumnNotFoundError
from .types import AggregateFunction, ArithmeticOperation, BooleanExpression, Predicate
from .utils import convert_sqlglot_type


def infer_type(node: Expression, scope: Scope) -> DataType:
    if node.type and node.type.this != SQLGlotDataType.Type.UNKNOWN:
        return convert_sqlglot_type(node.type)

    match node:
        case Alias():
            return infer_type(node.this, scope)

        case Column():
            t = scope.tables.resolve_column(node)
            if t is None:
                raise ColumnNotFoundError.from_column(node)
            else:
                return t

        case expr if isinstance(expr, BooleanExpression | Predicate):
            return DataType.BOOLEAN

        case expr if isinstance(expr, AggregateFunction):
            return DataType.NUMERIC

        case expr if isinstance(expr, ArithmeticOperation):
            return DataType.NUMERIC

    raise NotImplementedError(f'Type inference not implemented for {type(node)}')
