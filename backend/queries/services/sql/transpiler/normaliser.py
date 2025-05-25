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
    def normalise(query: SQLQuery) -> None:
        if isinstance(query, Select) and query.find(Select):
            SQLQueryNormaliser._normalise_subqueries(query)
            # SQLQueryNormaliser._convert_to_dnf_union(query)
        elif isinstance(query, SetOperation):
            SQLQueryNormaliser.normalise(query.left)
            SQLQueryNormaliser.normalise(query.right)

    @staticmethod
    def _normalise_subqueries(query: SQLQuery) -> None:
        def transform_node(node: Expression) -> Expression:
            match node:
                case In():
                    return SQLQueryNormaliser._transform_in(node)

                case comp if isinstance(comp, Comparison):
                    return SQLQueryNormaliser._transform_comparison(comp)

                case _:
                    return node

        query.transform(transform_node, copy=False)

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
        subquery = comp.right.this

        match comp.right:
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
                        left=left, subquery=subquery, comp=inverse[type(comp)]
                    )
                )

            case Any():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=subquery, comp=type(comp)
                )

            case Subquery():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=subquery, comp=type(comp)
                )

            case _:
                return comp  # Not a subquery, leave as is

    @staticmethod
    def _transform_subquery(subquery: SQLQuery, left: Expression, comp: type[Comparison]) -> Exists:
        def find_column(query: SQLQuery | Subquery) -> Expression:  # type: ignore[return]
            match query:
                case Select():
                    [column] = query.expressions
                    return cast(Expression, column)

                case query if isinstance(query, SetOperation):
                    return find_column(query.left)

                case Subquery():
                    return find_column(query.this)

        def to_select(subquery: SQLQuery | Subquery) -> Select:  # type: ignore[return]
            match subquery:
                case Select():
                    return subquery

                case subquery if isinstance(subquery, SetOperation):
                    return select('*').from_(subquery.subquery('sub'))

                case Subquery():
                    return to_select(subquery.this)

        select_ = to_select(subquery)
        condition = comp(this=left, expression=find_column(subquery))

        if select_.args.get('group'):
            select_ = select_.having(condition)
        else:
            select_ = select_.where(condition)

        return Exists(this=select_)
