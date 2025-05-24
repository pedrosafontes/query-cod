from typing import cast

from queries.services.types import SQLQuery
from sqlglot import exp
from sqlglot.expressions import (
    All,
    Any,
    Exists,
    Expression,
    In,
    Select,
    SetOperation,
    Subquery,
    not_,
    select,
)

from ..types import Comparison


class SQLQueryNormaliser:
    @staticmethod
    def normalise(query: SQLQuery) -> SQLQuery:
        transformed = SQLQueryNormaliser._normalise_subqueries(query)
        # transformed = SQLQueryNormaliser._convert_to_dnf_union(transformed)

        return transformed

    @staticmethod
    def _normalise_subqueries(query: SQLQuery) -> SQLQuery:
        @staticmethod
        def transform_node(node: Expression) -> Expression:
            match node:
                case In():
                    return SQLQueryNormaliser._transform_in(node)

                case comp if isinstance(comp, Comparison):
                    return SQLQueryNormaliser._transform_comparison(comp)

                case _:
                    return node

        return cast(SQLQuery, query.transform(transform_node))

    @staticmethod
    def _transform_in(in_: In) -> In | Exists:
        left = in_.this

        if not (subquery := in_.args.get('query')):
            return in_  # Not a subquery, leave as is

        if isinstance(subquery, Subquery):
            # Unwrap the subquery
            subquery = subquery.this

        return SQLQueryNormaliser._transform_subquery(subquery=subquery, left=left, comp=exp.EQ)

    @staticmethod
    def _transform_comparison(comp: Comparison) -> Expression:
        left = comp.left
        right = comp.right

        match right:
            case All():
                inverse: dict[type[Comparison], type[Comparison]] = {
                    exp.GT: exp.LTE,
                    exp.GTE: exp.LT,
                    exp.LT: exp.GTE,
                    exp.LTE: exp.GT,
                    exp.EQ: exp.NEQ,
                    exp.NEQ: exp.EQ,
                }

                return not_(
                    SQLQueryNormaliser._transform_subquery(
                        left=left, subquery=right.this, comp=inverse[type(comp)]
                    )
                )

            case Any():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=right.this, comp=type(comp)
                )

            case Subquery():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=right.this, comp=type(comp)
                )

            case _:
                return comp  # Not a subquery, leave as is

    @staticmethod
    def _transform_subquery(subquery: SQLQuery, left: Expression, comp: type[Comparison]) -> Exists:
        [column] = subquery.expressions

        condition = comp(this=left, expression=column)

        if isinstance(subquery, SetOperation):
            select_ = select('*').from_(subquery.subquery('sub'))
        elif isinstance(subquery, Select):
            select_ = subquery

        if select_.args.get('group'):
            select_ = select_.having(condition)
        else:
            select_ = select_.where(condition)

        return Exists(this=select_)
