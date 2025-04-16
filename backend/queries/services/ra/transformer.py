from typing import Any

from lark import Token, Transformer

from .ast import (
    Aggregation,
    AggregationFunction,
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonOperator,
    ComparisonValue,
    Division,
    GroupedAggregation,
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
    TopN,
)


class RATransformer(Transformer[Relation, RAExpression]):
    def relation(self, args: list[Token]) -> Relation:
        return Relation(name=args[0].value, attributes=[])

    def attribute(self, args: tuple[Token] | tuple[Relation | Token]) -> Attribute:  # type: ignore[return]
        match args:
            case (relation, token):
                return Attribute(name=token.value, relation=relation.name)  # type: ignore[union-attr]
            case (token,):
                return Attribute(name=token.value)  # type: ignore[union-attr]

    def projection(self, args: tuple[list[Attribute], RAExpression]) -> Projection:
        attrs, expr = args
        return Projection(attributes=attrs, expression=expr)

    def selection(self, args: tuple[BooleanExpression, RAExpression]) -> Selection:
        condition, expr = args
        return Selection(condition=condition, expression=expr)

    def grouped_aggregation(
        self, args: tuple[list[Attribute], list[Aggregation], RAExpression]
    ) -> GroupedAggregation:
        group_by, aggregations, expr = args
        return GroupedAggregation(group_by=group_by, aggregations=aggregations, expression=expr)

    def aggregation(self, args: tuple[Attribute, AggregationFunction, Attribute]) -> Aggregation:
        return Aggregation(
            input=args[0],
            aggregation_function=args[1],
            output=args[2].name,
        )

    def count(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.COUNT

    def sum_(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.SUM

    def avg(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.AVG

    def min_(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.MIN

    def max_(self, _: tuple[()]) -> AggregationFunction:
        return AggregationFunction.MAX

    def topn(self, args: tuple[Token, Attribute, RAExpression]) -> TopN:
        limit, attr, expr = args
        return TopN(limit=int(limit), attribute=attr, expression=expr)

    def union(self, args: tuple[RAExpression, RAExpression]) -> SetOperation:
        return SetOperation(operator=SetOperator.UNION, left=args[0], right=args[1])

    def difference(self, args: tuple[RAExpression, RAExpression]) -> SetOperation:
        return SetOperation(operator=SetOperator.DIFFERENCE, left=args[0], right=args[1])

    def intersection(self, args: tuple[RAExpression, RAExpression]) -> SetOperation:
        return SetOperation(operator=SetOperator.INTERSECT, left=args[0], right=args[1])

    def cartesian(self, args: tuple[RAExpression, RAExpression]) -> SetOperation:
        return SetOperation(operator=SetOperator.CARTESIAN, left=args[0], right=args[1])

    def natural_join(self, args: tuple[RAExpression, RAExpression]) -> Join:
        return Join(operator=JoinOperator.NATURAL, left=args[0], right=args[1])

    def semi_join(self, args: tuple[RAExpression, RAExpression]) -> Join:
        return Join(operator=JoinOperator.SEMI, left=args[0], right=args[1])

    def theta_join(self, args: tuple[RAExpression, BooleanExpression, RAExpression]) -> ThetaJoin:
        left, condition, right = args
        return ThetaJoin(left=left, right=right, condition=condition)

    def division(self, args: tuple[RAExpression, RAExpression]) -> Division:
        return Division(dividend=args[0], divisor=args[1])

    def and_(self, args: tuple[BooleanExpression, BooleanExpression]) -> BinaryBooleanExpression:
        left, right = args
        return BinaryBooleanExpression(operator=BinaryBooleanOperator.AND, left=left, right=right)

    def or_(self, args: tuple[BooleanExpression, BooleanExpression]) -> BinaryBooleanExpression:
        left, right = args
        return BinaryBooleanExpression(operator=BinaryBooleanOperator.OR, left=left, right=right)

    def not_(self, args: tuple[BooleanExpression]) -> NotExpression:
        return NotExpression(expression=args[0])

    def comparison(
        self, args: tuple[ComparisonValue, ComparisonOperator, ComparisonValue]
    ) -> Comparison:
        return Comparison(left=args[0], operator=args[1], right=args[2])

    def eq(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.EQUAL

    def neq(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.NOT_EQUAL

    def lt(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.LESS_THAN

    def leq(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.LESS_THAN_EQUAL

    def gt(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.GREATER_THAN

    def geq(self, _: tuple[()]) -> ComparisonOperator:
        return ComparisonOperator.GREATER_THAN_EQUAL

    def number(self, args: list[Token]) -> int:
        return int(args[0])

    def string(self, args: list[Token]) -> str:
        return str(args[0])[1:-1]  # strip quotes

    def item_list(self, args: list[Any]) -> list[Any]:
        return args

    def _subscript(self, args: list[Any]) -> Any:
        return args[0]

    def _overset(self, args: list[Any]) -> tuple[Any, Any]:
        return args[0], args[1]

    def expr(self, args: list[Any]) -> Any:
        return args[0]

    def sub_expr(self, args: list[Any]) -> Any:
        return args[0]
