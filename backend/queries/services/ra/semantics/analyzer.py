from collections.abc import Callable

from databases.types import DataType, Schema

from ..parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BooleanExpression,
    Comparison,
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
    DivisionSchemaMismatchError,
    DivisionTypeMismatchError,
    InvalidFunctionArgumentError,
    JoinAttributeTypeMismatchError,
    TypeMismatchError,
    UndefinedAttributeError,
    UndefinedRelationError,
    UnionCompatibilityError,
)
from .types import TypedAttribute
from .utils import are_types_compatible, type_of_function, type_of_value


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
            raise UndefinedRelationError(rel, rel.name)

        return [
            TypedAttribute(attr, relations={rel.name}, data_type=data_type)
            for attr, data_type in attrs.items()
        ]

    def _validate_Projection(self, proj: Projection) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(proj.expression)
        return [self._resolve_attribute(attr, input_attrs) for attr in proj.attributes]

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
                    raise UnionCompatibilityError(op, op.operator, left_attrs, right_attrs)

                return [TypedAttribute(name=a.name, data_type=a.data_type) for a in left_attrs]

    def _validate_Join(self, join: Join) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)
        return self._merge_schemas(join, left_attrs, right_attrs)

    def _validate_ThetaJoin(self, join: ThetaJoin) -> list[TypedAttribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)
        self._validate_condition(join.condition, left_attrs + right_attrs)
        return self._merge_schemas(join, left_attrs, right_attrs)

    def _validate_Division(self, div: Division) -> list[TypedAttribute]:  # noqa: N802
        dividend_attrs = self._validate(div.dividend)
        divisor_attrs = self._validate(div.divisor)

        dividend_lookup = {a.name: a for a in dividend_attrs}

        for attr in divisor_attrs:
            match = dividend_lookup.get(attr.name)
            if match is None:
                raise DivisionSchemaMismatchError(div, dividend_attrs, divisor_attrs)
            if match.data_type != attr.data_type:
                raise DivisionTypeMismatchError(div, match, attr)

        divisor_attr_names = {b.name for b in divisor_attrs}
        return [a for a in dividend_attrs if a.name not in divisor_attr_names]

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(agg.expression)

        # Validate group by attributes
        for attr in agg.group_by:
            self._resolve_attribute(attr, input_attrs)

        # Validate aggregation functions and their arguments
        for a in agg.aggregations:
            input_attr = self._resolve_attribute(a.input, input_attrs)
            input_types, _ = type_of_function(a.aggregation_function, input_attr)

            if input_attr.data_type not in input_types:
                raise InvalidFunctionArgumentError(
                    source=agg,
                    function=a.aggregation_function,
                    expected=input_types,
                    actual=input_attr.data_type,
                )

        return self._compute_aggregation_schema(agg, input_attrs)

    def _validate_TopN(self, top: TopN) -> list[TypedAttribute]:  # noqa: N802
        input_attrs = self._validate(top.expression)
        self._resolve_attribute(top.attribute, input_attrs)
        return input_attrs

    def _validate_condition(self, cond: BooleanExpression, attrs: list[TypedAttribute]) -> None:
        match cond:
            case Attribute():
                typed_attr = self._resolve_attribute(cond, attrs)
                if typed_attr.data_type != DataType.BOOLEAN:
                    raise TypeMismatchError(cond, DataType.BOOLEAN, typed_attr.data_type)

            case Comparison():
                self._validate_comparison(cond, attrs)

            case BinaryBooleanExpression(left=left, right=right):
                self._validate_condition(left, attrs)
                self._validate_condition(right, attrs)

            case NotExpression(expression=inner):
                self._validate_condition(inner, attrs)

    def _validate_comparison(self, cond: Comparison, attrs: list[TypedAttribute]) -> None:
        types: list[DataType] = []

        for side in (cond.left, cond.right):
            if isinstance(side, Attribute):
                typed_attr = self._resolve_attribute(side, attrs)
                types.append(typed_attr.data_type)
            else:
                types.append(type_of_value(side))

        left_type, right_type = types
        if not are_types_compatible(left_type, right_type):
            raise TypeMismatchError(cond, left_type, right_type)

    def _resolve_attribute(self, attr: Attribute, context: list[TypedAttribute]) -> TypedAttribute:
        matches = [
            a
            for a in context
            if a.name == attr.name
            and (attr.relation is None or (a.relations and attr.relation in a.relations))
        ]
        if not matches:
            raise UndefinedAttributeError(attr, attr)
        if len(matches) > 1 and attr.relation is None:
            raise AmbiguousAttributeError(
                attr, attr.name, [a.relations for a in matches if a.relations is not None]
            )
        return matches[0]

    def _merge_schemas(
        self,
        join: Join | ThetaJoin,
        left_attrs: list[TypedAttribute],
        right_attrs: list[TypedAttribute],
    ) -> list[TypedAttribute]:
        merged: dict[str, TypedAttribute] = {}

        for attr in left_attrs + right_attrs:
            if attr.name in merged:
                existing = merged[attr.name]
                if attr.data_type != existing.data_type:
                    raise JoinAttributeTypeMismatchError(join, existing, attr)

                # Merge relation sets
                existing.relations = (existing.relations or set()).union(attr.relations or set())
            else:
                # Copy to avoid modifying the original
                merged[attr.name] = TypedAttribute(
                    name=attr.name,
                    data_type=attr.data_type,
                    relations=attr.relations,
                )

        return list(merged.values())

    def _compute_aggregation_schema(
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
            _, output_type = type_of_function(a.aggregation_function, input_attr)
            aggregation_attrs.append(
                TypedAttribute(
                    name=a.output,
                    data_type=output_type,
                )
            )

        return aggregation_attrs + group_by_attrs
