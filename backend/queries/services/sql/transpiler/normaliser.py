from typing import cast

from queries.services.types import SQLQuery
from sqlglot import exp
from sqlglot.expressions import (
    All,
    Any,
    Exists,
    Expression,
    In,
    Or,
    Select,
    SetOperation,
    Subquery,
    not_,
    select,
    union,
)
from sqlglot.optimizer.normalize import normalize

from ..types import Comparison


class SQLQueryNormaliser:
    @staticmethod
    def normalise(query: SQLQuery) -> SQLQuery:
        transformed = SQLQueryNormaliser.normalise_subqueries(query)
        transformed = SQLQueryNormaliser.normalise_conditions(transformed)
        return transformed

    @staticmethod
    def normalise_subqueries(query: SQLQuery) -> SQLQuery:
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

    @staticmethod
    def normalise_conditions(query: SQLQuery) -> SQLQuery:
        def transform_select(node: Expression) -> Expression:
            if isinstance(node, Select):
                where: Expression | None = node.args.get('where')
                if where and where.find(Select):
                    return SQLQueryNormaliser.convert_to_dnf_union(node)
            return node

        return cast(SQLQuery, query.transform(transform_select))

    @staticmethod
    def convert_to_dnf_union(select: Select) -> SQLQuery:
        conjunctions = SQLQueryNormaliser._extract_dnf_conjunctions(select.args['where'].this)
        if len(conjunctions) > 1:
            return union(*[select.where(conjunction, append=False) for conjunction in conjunctions])
        else:
            return select

    @staticmethod
    def _extract_dnf_conjunctions(where: Expression) -> list[Expression]:
        dnf = normalize(where, dnf=True)

        if isinstance(dnf, Or):
            return list(dnf.flatten())  # type: ignore[no-untyped-call]
        else:
            # The expression is a single conjunction
            return [dnf]
