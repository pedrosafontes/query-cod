from collections.abc import Callable

from databases.types import DataType, Schema

from ..parser.ast import (
    AggregationFunction,
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    Comparison,
    ComparisonValue,
    Division,
    GroupedAggregation,
    Join,
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
from .errors import (
    AmbiguousAttributeError,
    InvalidFunctionArgumentError,
    JoinAttributeTypeMismatchError,
    TypeMismatchError,
    UndefinedAttributeError,
    UndefinedRelationError,
    UnionCompatibilityError,
)
from .types import TypedAttribute


class RASemanticAnalyzer:
    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, expr: RAExpression) -> None:
        self._validate(expr)

    def _validate(self, expr: RAExpression) -> list[TypedAttribute]:
        method: Callable[[RAExpression], list[TypedAttribute]] = getattr(
            self, f'_validate_{type(expr).__name__}'
        )
        return method(expr)

    def _validate_Relation(self, rel: Relation) -> list[TypedAttribute]:  # noqa: N802
        attrs = self.schema.get(rel.name)
        if attrs is None:
            raise UndefinedRelationError(rel.name)

        return [
            TypedAttribute(attr, relations={rel.name}, data_type=data_type)
            for attr, data_type in attrs.items()
        ]

    def _validate_Projection(self, proj: Projection) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(proj.expression)
        output_attrs = []
        for attr in proj.attributes:
            output_attrs.append(self._resolve_attribute(attr, input_attrs))

        return output_attrs

    def _validate_Selection(self, sel: Selection) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(sel.expression)
        self._validate_condition(sel.condition, input_attrs)
        return input_attrs

    def _validate_SetOperation(self, op: SetOperation) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(op.left)
        right_attrs = self._validate(op.right)

        match op.operator:
            case SetOperator.CARTESIAN:
                return left_attrs + right_attrs
            case _:
                union_compatible = all(
                    a.name == b.name and a.data_type == b.data_type
                    for a, b in zip(
                        sorted(left_attrs, key=lambda a: a.name),
                        sorted(right_attrs, key=lambda a: a.name),
                        strict=False,
                    )
                )

                if not union_compatible:
                    raise UnionCompatibilityError(op.left, op.right)

                return [TypedAttribute(name=a.name, data_type=a.data_type) for a in left_attrs]

    def _validate_Join(self, join: Join) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)

        merged: dict[str, TypedAttribute] = {}

        for attr in left_attrs + right_attrs:
            if attr.name in merged:
                existing = merged[attr.name]
                if attr.data_type != existing.data_type:
                    raise JoinAttributeTypeMismatchError(attr, existing)

                existing.relations = (existing.relations or set()).union(attr.relations or set())
            else:
                merged[attr.name] = TypedAttribute(
                    name=attr.name,
                    data_type=attr.data_type,
                    relations=attr.relations,
                )

        return list(merged.values())

    def _validate_ThetaJoin(self, join: ThetaJoin) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)
        join_attrs = left_attrs + right_attrs
        self._validate_condition(join.condition, join_attrs)

        return join_attrs

    def _validate_Division(self, div: Division) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(div.dividend)
        right_attrs = self._validate(div.divisor)

        return [a for a in left_attrs if not any(a.name == b.name for b in right_attrs)]

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(agg.expression)
        for attr in agg.group_by:
            self._resolve_attribute(attr, input_attrs)
        for a in agg.aggregations:
            input_attr = self._resolve_attribute(a.input, input_attrs)
            input_types, _ = self._type_of_function(a.aggregation_function, input_attr)
            if input_attr.data_type not in input_types:
                raise InvalidFunctionArgumentError(
                    function=a.aggregation_function,
                    expected=input_types,
                    actual=input_attr.data_type,
                )

        return self._grouped_aggregation_attributes(agg, input_attrs)

    def _grouped_aggregation_attributes(
        self, agg: GroupedAggregation, input_attrs: list[TypedAttribute]
    ) -> list[TypedAttribute]:
        group_by_attrs = list(
            filter(
                lambda a: any(a.name == b.name for b in agg.group_by),
                input_attrs,
            )
        )

        aggregation_attrs = []
        for a in agg.aggregations:
            input_attr = self._resolve_attribute(a.input, input_attrs)
            _, output_type = self._type_of_function(a.aggregation_function, input_attr)
            aggregation_attrs.append(
                TypedAttribute(
                    name=a.output,
                    data_type=output_type,
                )
            )

        return aggregation_attrs + group_by_attrs

    def _type_of_function(
        self, func: AggregationFunction, attr: TypedAttribute
    ) -> tuple[list[DataType], DataType]:
        input_type = attr.data_type
        match func:
            case AggregationFunction.COUNT:
                return ([input_type], DataType.INTEGER)
            case AggregationFunction.SUM | AggregationFunction.AVG:
                return ([DataType.INTEGER, DataType.FLOAT], DataType.FLOAT)
            case AggregationFunction.MIN | AggregationFunction.MAX:
                return ([input_type], input_type)
            case _:
                raise NotImplementedError(f'Unknown aggregation function: {func}')

    def _validate_TopN(self, top: TopN) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(top.expression)
        self._resolve_attribute(top.attribute, input_attrs)

        return input_attrs

    def _validate_condition(self, cond: BooleanExpression, attrs: list[TypedAttribute]) -> None:
        if isinstance(cond, Comparison):
            types: list[DataType] = []
            for side in (cond.left, cond.right):
                if isinstance(side, Attribute):
                    typed_attr = self._resolve_attribute(side, attrs)
                    types.append(typed_attr.data_type)
                else:
                    types.append(self._type_of_value(side))
            left_t, right_t = types
            if not self._types_are_comparable(left_t, right_t):
                raise TypeMismatchError(left_t, right_t)
        elif isinstance(cond, BinaryBooleanExpression):
            self._validate_condition(cond.left, attrs)
            self._validate_condition(cond.right, attrs)
        elif isinstance(cond, NotExpression):
            self._validate_condition(cond.expression, attrs)

    def _type_of_value(self, value: ComparisonValue) -> DataType:
        match value:
            case int():
                return DataType.INTEGER
            case float():
                return DataType.FLOAT
            case str():
                return DataType.STRING
            case bool():
                return DataType.BOOLEAN
            case _:
                raise NotImplementedError(f'Unknown type: {type(value)}')

    def _types_are_comparable(self, left: DataType, right: DataType) -> bool:
        return (
            left == right
            or (left == DataType.INTEGER and right == DataType.FLOAT)
            or (left == DataType.FLOAT and right == DataType.INTEGER)
        )

    def _resolve_attribute(self, attr: Attribute, context: list[TypedAttribute]) -> TypedAttribute:
        matches = [
            a
            for a in context
            if a.name == attr.name
            and (attr.relation is None or (a.relations and attr.relation in a.relations))
        ]
        if not matches:
            raise UndefinedAttributeError(attr.name)
        if len(matches) > 1 and attr.relation is None:
            raise AmbiguousAttributeError(
                attr.name, [a.relations for a in matches if a.relations is not None]
            )
        return matches[0]
