from collections.abc import Callable

from queries.services.types import RelationalSchema
from sqlglot.expressions import (
    EQ,
    Except,
    Exists,
    ExpOrStr,
    Intersect,
    Select,
    Union,
    and_,
    column,
    not_,
    or_,
    select,
    subquery,
)

from ..parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Join,
    JoinOperator,
    NotExpression,
    Projection,
    RAExpression,
    Relation,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
)
from ..shared.inference import SchemaInferrer
from .renamer import RAExpressionRenamer


class RAtoSQLTranspiler:
    def __init__(self, schema: RelationalSchema):
        self._schema_inferrer = SchemaInferrer(schema)

    def transpile(self, expr: RAExpression) -> Select | Union | Intersect | Except:
        method: Callable[[RAExpression], Select] = getattr(
            self, f'_transpile_{type(expr).__name__}'
        )
        return method(expr)

    def _transpile_Relation(self, rel: Relation) -> Select:  # noqa: N802
        return select('*').from_(rel.name)

    def _transpile_Projection(self, proj: Projection) -> Select:  # noqa: N802
        query = self._transpile_select(proj.expression)
        query.set('expressions', [])
        return query.select(*[attr.name for attr in proj.attributes])

    def _transpile_Selection(self, selection: Selection) -> Select:  # noqa: N802
        query = self._transpile_select(selection.expression)
        condition = self._transpile_condition(selection.condition)
        if query.args.get('group_by'):
            return query.having(condition)
        else:
            return query.where(condition)

    def _transpile_condition(self, cond: BooleanExpression) -> ExpOrStr:
        match cond:
            case BinaryBooleanExpression():
                left = self._transpile_condition(cond.left)
                right = self._transpile_condition(cond.right)
                match cond.operator:
                    case BinaryBooleanOperator.AND:
                        return and_(left, right)
                    case BinaryBooleanOperator.OR:
                        return or_(left, right)
            case NotExpression():
                return not_(self._transpile_condition(cond.expression))
            case Comparison():
                left = self._transpile_comparison_value(cond.left)
                right = self._transpile_comparison_value(cond.right)
                return f'{left} {cond.operator} {right}'
            case Attribute() as attr:
                return EQ(this=column(attr.name, table=attr.relation), expression='TRUE')

    def _transpile_comparison_value(self, comparison: ComparisonValue) -> str:
        if isinstance(comparison, str):
            return f"'{comparison}'"
        else:
            return str(comparison)

    def _transpile_SetOperation(self, op: SetOperation) -> Select | Union | Intersect | Except:  # noqa: N802
        left = self.transpile(op.left)
        right = self.transpile(op.right)
        expr: Select | Union | Intersect | Except
        match op.operator:
            case SetOperator.UNION:
                expr = left.union(right)
            case SetOperator.INTERSECT:
                expr = left.intersect(right)
            case SetOperator.DIFFERENCE:
                expr = left.except_(right)
            case SetOperator.CARTESIAN:
                left = self._transpile_select(op.left)
                if isinstance(op.right, Relation):
                    # op.right is a base table
                    return left.join(op.right.name, join_type='CROSS')
                else:
                    # right is a derived relation
                    return left.join(right, join_type='CROSS', join_alias='r')
        return expr

    def _transpile_Join(self, join: Join) -> Select:  # noqa: N802
        left, left_alias = self._maybe_subquery(join.left, alias='l')

        match join.operator:
            case JoinOperator.NATURAL:
                if isinstance(join.right, Relation):
                    # join.right is a base table
                    return left.join(join.right.name, join_type='NATURAL')
                else:
                    # right is a derived relation
                    right = self.transpile(join.right)
                    return left.join(right, join_type='NATURAL', join_alias='r')
            case JoinOperator.SEMI:
                right, right_alias = self._maybe_subquery(join.right, 'r')

                left_output = self._schema_inferrer.infer(join.left)
                right_output = self._schema_inferrer.infer(join.right)

                left_names = {attr.name for attr in left_output.attrs}
                right_names = {attr.name for attr in right_output.attrs}
                shared_names = left_names & right_names

                return left.where(
                    Exists(
                        this=right.where(
                            *[
                                f'{left_alias}.{name} = {right_alias}.{name}'
                                for name in shared_names
                            ]
                        )
                    )
                )

    def _transpile_ThetaJoin(self, join: ThetaJoin) -> Select:  # noqa: N802
        left, left_alias = self._maybe_subquery(join.left, 'l')

        # rename the attributes in the left relation to use the alias
        left_schema = self._schema_inferrer.infer(join.left).schema
        renamings = {}
        for table in left_schema.keys():
            if table:
                renamings[table] = left_alias

        if isinstance(join.right, Relation):
            # right is a base table
            join_query = left.join(join.right.name, join_type='CROSS')
        else:
            # right is a derived relation
            right = self.transpile(join.right)
            right_alias = 'r'

            # rename the attributes in the right relation to use the alias
            right_schema = self._schema_inferrer.infer(join.right).schema
            for table in right_schema.keys():
                if table:
                    renamings[table] = right_alias

            join_query = left.join(right, join_type='CROSS', join_alias=right_alias)

        renamed_condition = RAExpressionRenamer(renamings).rename_condition(join.condition)
        return join_query.where(self._transpile_condition(renamed_condition))

    def _maybe_subquery(self, expr: RAExpression, alias: str) -> tuple[Select, str]:
        if isinstance(expr, Relation):
            return self._transpile_select(expr), expr.name
        else:
            return subquery(self._transpile_select(expr), alias).select('*'), alias

    def _transpile_select(self, expr: RAExpression) -> Select:
        query = self.transpile(expr)
        if isinstance(query, Select):
            return query
        else:
            return subquery(query, 'set_op').select('*')
