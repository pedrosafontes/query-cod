from typing import Any, cast

from lark import Token, Transformer, Tree

from .ast import (
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NEQ,
    Aggregation,
    AggregationFunction,
    And,
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
    Not,
    Or,
    Projection,
    RAQuery,
    Relation,
    Selection,
    SetOperation,
    ThetaJoin,
    TopN,
)


class RATransformer(Transformer[Relation, RAQuery]):
    def _transform_tree(self, tree: Tree[Relation]) -> RAQuery:
        node = super()._transform_tree(tree)  # type: ignore[no-untyped-call]
        if isinstance(node, RAQuery):
            node.position = {
                'line': tree.meta.line,
                'start_col': tree.meta.column,
                'end_col': tree.meta.end_column,
            }
        return cast(RAQuery, node)

    def relation(self, args: list[str]) -> Relation:
        return Relation(name=self._identifier(args[0]))

    def attribute(self, args: tuple[str] | tuple[Relation, str]) -> Attribute:  # type: ignore[return]
        match args:
            case (Relation() as relation, str() as identifier):
                name = self._identifier(identifier)
                return Attribute(name=name, relation=relation.name)
            case (str() as identifier,):
                name = self._identifier(identifier)
                return Attribute(name=name)

    def _identifier(self, ident: str) -> str:
        return ident.replace('\\', '')

    def projection(self, args: tuple[list[Attribute], RAQuery]) -> Projection:
        attrs, query = args
        return query.project(attrs, optimise=False)

    def selection(self, args: tuple[BooleanExpression, RAQuery]) -> Selection:
        condition, query = args
        return query.select(condition)

    def grouped_aggregation(
        self, args: tuple[list[Attribute], list[Aggregation], RAQuery]
    ) -> GroupedAggregation:
        group_by, aggregations, query = args
        return query.grouped_aggregation(group_by, aggregations)

    def aggregation(self, args: tuple[Attribute, AggregationFunction, Attribute]) -> Aggregation:
        input_, aggregation_function, output = args
        return Aggregation(
            input=input_,
            aggregation_function=aggregation_function,
            output=output.name,
        )

    def count(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.COUNT

    def sum(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.SUM

    def avg(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.AVG

    def min(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.MIN

    def max(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.MAX

    def topn(self, args: tuple[Token, Attribute, RAQuery]) -> TopN:
        limit, attr, query = args
        return query.top_n(int(limit), attr)

    def union(self, args: tuple[RAQuery, RAQuery]) -> SetOperation:
        left, right = args
        return left.union(right)

    def difference(self, args: tuple[RAQuery, RAQuery]) -> SetOperation:
        left, right = args
        return left.difference(right)

    def intersection(self, args: tuple[RAQuery, RAQuery]) -> SetOperation:
        left, right = args
        return left.intersect(right)

    def cartesian(self, args: tuple[RAQuery, RAQuery]) -> SetOperation:
        left, right = args
        return left.cartesian(right)

    def natural_join(self, args: tuple[RAQuery, RAQuery]) -> Join:
        left, right = args
        return left.natural_join(right)

    def semi_join(self, args: tuple[RAQuery, RAQuery]) -> Join:
        left, right = args
        return left.semi_join(right)

    def theta_join(self, args: tuple[RAQuery, BooleanExpression, RAQuery]) -> ThetaJoin:
        left, condition, right = args
        return left.theta_join(right, condition)

    def division(self, args: tuple[RAQuery, RAQuery]) -> Division:
        dividend, divisor = args
        return dividend.divide(divisor)

    def and_(self, args: tuple[BooleanExpression, BooleanExpression]) -> BinaryBooleanExpression:
        return And(*args)

    def or_(self, args: tuple[BooleanExpression, BooleanExpression]) -> BinaryBooleanExpression:
        return Or(*args)

    def not_(self, args: tuple[BooleanExpression]) -> Not:
        return Not(*args)

    def eq(self, args: tuple[ComparisonValue, ComparisonValue]) -> EQ:
        return EQ(*args)

    def neq(self, args: tuple[ComparisonValue, ComparisonValue]) -> NEQ:
        return NEQ(*args)

    def lt(self, args: tuple[ComparisonValue, ComparisonValue]) -> LT:
        return LT(*args)

    def leq(self, args: tuple[ComparisonValue, ComparisonValue]) -> LTE:
        return LTE(*args)

    def gt(self, args: tuple[ComparisonValue, ComparisonValue]) -> GT:
        return GT(*args)

    def geq(self, args: tuple[ComparisonValue, ComparisonValue]) -> GTE:
        return GTE(*args)

    def int(self, args: list[Token]) -> int:
        return int(args[0])

    def float(self, args: list[Token]) -> float:
        return float(args[0])

    def string(self, args: list[Token]) -> str:
        return args[0]

    def item_list(self, args: list[Any]) -> list[Any]:
        return args

    def query(self, args: tuple[RAQuery]) -> RAQuery:
        return args[0]

    def subquery(self, args: tuple[RAQuery]) -> RAQuery:
        return args[0]

    def IDENT(self, token: Token) -> str:  # noqa: N802
        return str(token.value)

    def CNAME(self, token: Token) -> str:  # noqa: N802
        return str(token.value)

    def ESCAPED_STRING(self, token: Token) -> str:  # noqa: N802
        return str(token.value)[1:-1]  # strip quotes
