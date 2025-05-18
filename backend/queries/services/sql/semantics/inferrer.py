from queries.services.sql.semantics.scope import Scope
from ra_sql_visualisation.types import DataType
from sqlglot.expressions import Alias, Column, Count, Expression
from sqlglot.expressions import DataType as SQLGlotDataType

from .errors.object_reference import ColumnNotFoundError
from .types import AggregateFunction, ArithmeticOperation, BooleanExpression, Predicate
from .utils import convert_sqlglot_type


class TypeInferrer:
    def __init__(self, scope: Scope) -> None:
        self.scope = scope

    def infer(self, node: Expression) -> DataType:
        if node.type and node.type.this != SQLGlotDataType.Type.UNKNOWN:
            return convert_sqlglot_type(node.type)

        match node:
            case Alias():
                return self.infer(node.this)

            case Column():
                t = self.scope.tables.resolve_column(node)
                if t is None:
                    raise ColumnNotFoundError.from_column(node)
                else:
                    return t

            case expr if isinstance(expr, BooleanExpression | Predicate):
                return DataType.BOOLEAN

            case agg if isinstance(expr, AggregateFunction):
                return self._infer_aggregate_type(agg)

            case expr if isinstance(expr, ArithmeticOperation):
                lt = self.infer(expr.left)
                rt = self.infer(expr.right)
                return DataType.dominant([lt, rt])

        raise NotImplementedError(f'Type inference not implemented for {type(node)}')

    def _infer_aggregate_type(self, agg: Expression) -> DataType:
        if isinstance(agg, Count):
            return DataType.INTEGER
        else:
            return self.infer(agg.this)
