from typing import cast

from queries.services.types import RelationalSchema, SQLQuery
from sqlglot import exp
from sqlglot.expressions import (
    All,
    Any,
    Column,
    Exists,
    Expression,
    In,
    Or,
    Select,
    SetOperation,
    Subquery,
    Table,
    column,
    not_,
    union,
)
from sqlglot.optimizer.normalize import normalize

from ..scope.builder import build_scope
from ..scope.query import SQLScope
from ..types import Comparison


class SQLQueryNormaliser:
    @staticmethod
    def normalise(query: SQLQuery, schema: RelationalSchema) -> SQLQuery:
        transformed = SQLQueryNormaliser.alias_tables(query)
        transformed = SQLQueryNormaliser.normalise_subqueries(transformed, schema)
        transformed = SQLQueryNormaliser.normalise_conditions(transformed)
        return transformed

    @staticmethod
    def alias_tables(query: SQLQuery) -> SQLQuery:
        table_counters: dict[str, int] = {}

        # Initialize counters
        for table in query.find_all(Table, Subquery):
            table_counters[table.alias_or_name] = 0

        def update_column_references(select: Select, name: str, alias: str) -> None:
            for col in select.find_all(Column):
                if col.table == name:
                    col.replace(column(col=col.name, table=alias))

        def get_unique_alias(name: str) -> str:
            while (alias := f'{name}{table_counters[name] - 1}') in table_counters:
                table_counters[name] += 1
            return alias

        def assign_aliases(node: Expression) -> Expression:
            if isinstance(node, Table):
                name = node.alias_or_name
                table_counters[name] += 1

                if table_counters[name] == 1:
                    return node

                alias = get_unique_alias(name)
                update_column_references(cast(Select, node.parent_select), name, alias)

                return node.as_(alias)

            return node

        return cast(SQLQuery, query.transform(assign_aliases))

    @staticmethod
    def normalise_subqueries(query: SQLQuery, schema: RelationalSchema) -> SQLQuery:
        scope = build_scope(query, schema)

        def transform_node(node: Expression) -> Expression:
            match node:
                case In():
                    return SQLQueryNormaliser._transform_in(node, scope)

                case comp if isinstance(comp, Comparison):
                    return SQLQueryNormaliser._transform_comparison(comp, scope)

                case _:
                    return node

        return cast(SQLQuery, query.transform(transform_node))

    @staticmethod
    def _transform_in(in_: In, scope: SQLScope) -> In | Exists:
        left = in_.this

        if not (subquery := in_.args.get('query')):
            return in_  # Not a subquery, leave as is

        if isinstance(subquery, Subquery):
            # Unwrap the subquery
            subquery = subquery.this

        return SQLQueryNormaliser._transform_subquery(
            subquery=subquery, left=left, comp=exp.EQ, scope=scope
        )

    @staticmethod
    def _transform_comparison(comp: Comparison, scope: SQLScope) -> Expression:
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
                        left=left, subquery=subquery, comp=inverse[type(comp)], scope=scope
                    )
                )

            case Any():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=subquery, comp=type(comp), scope=scope
                )

            case Subquery():
                return SQLQueryNormaliser._transform_subquery(
                    left=left, subquery=subquery, comp=type(comp), scope=scope
                )

            case _:
                return comp  # Not a subquery, leave as is

    @staticmethod
    def _transform_subquery(
        subquery: SQLQuery | Subquery, left: Expression, comp: type[Comparison], scope: SQLScope
    ) -> Exists:
        def to_select(subquery: SQLQuery | Subquery) -> Select:  # type: ignore[return]
            match subquery:
                case Select():
                    return subquery

                case Subquery():
                    return to_select(subquery.this)

                case subquery if isinstance(subquery, SetOperation):
                    raise NotImplementedError('Set operations are not supported')

        select_ = to_select(subquery)
        qualified = cast(Select, SQLQueryNormaliser.qualify(select_, scope))
        condition = comp(
            this=SQLQueryNormaliser.qualify(left, scope), expression=qualified.expressions[0]
        )

        if qualified.args.get('group'):
            qualified = qualified.having(condition)
        else:
            qualified = qualified.where(condition)

        return Exists(this=qualified)

    @staticmethod
    def qualify(expr: Expression, parent_scope: SQLScope) -> Expression:
        scope = parent_scope.find(expr)

        if not scope:
            raise ValueError('Expression scope not found in the provided SQL scope.')

        def qualify_column(expr: Expression) -> Expression:
            if isinstance(expr, Column):
                source = scope.tables.find_column_source(expr)
                assert source  # noqa: S101
                return column(col=expr.name, table=source.name)
            return expr

        return expr.transform(qualify_column)

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
