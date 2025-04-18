from collections.abc import Callable

from databases.types import Schema

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
    ThetaJoin,
    TopN,
)
from .errors import (
    AmbiguousAttributeError,
    RAValidationError,
    UnknownAttributeError,
    UnknownRelationError,
)


class RASemanticAnalyzer:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.errors: list[RAValidationError] = []

    def validate(self, expr: RAExpression) -> list[RAValidationError]:
        self.errors = []
        self._validate(expr)
        return self.errors

    def _validate(self, expr: RAExpression) -> list[Attribute]:
        method: Callable[[RAExpression], list[Attribute]] = getattr(
            self, f'_validate_{type(expr).__name__}'
        )
        return method(expr)

    def _validate_Relation(self, rel: Relation) -> list[Attribute]:  # noqa: N802
        if rel.name not in self.schema:
            self.errors.append(UnknownRelationError(rel.name))

        return [Attribute(name, relation=rel.name) for name in self.schema.get(rel.name, [])]

    def _validate_Projection(self, proj: Projection) -> list[Attribute]:  # noqa: N802
        input_attrs = self._validate(proj.expression)
        for attr in proj.attributes:
            matches = [
                a
                for a in input_attrs
                if a.name == attr.name and (attr.relation is None or a.relation == attr.relation)
            ]
            if not matches:
                self.errors.append(UnknownAttributeError(attr.name))

        return proj.attributes

    def _validate_Selection(self, sel: Selection) -> list[Attribute]:  # noqa: N802
        input_attrs = self._validate(sel.expression)
        self._validate_condition(sel.condition, input_attrs)
        return input_attrs

    def _validate_SetOperation(self, op: SetOperation) -> list[Attribute]:  # noqa: N802
        left_attrs = self._validate(op.left)
        self._validate(op.right)

        return left_attrs

    def _validate_Join(self, join: Join) -> list[Attribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)

        return left_attrs + right_attrs

    def _validate_ThetaJoin(self, join: ThetaJoin) -> list[Attribute]:  # noqa: N802
        left_attrs = self._validate(join.left)
        right_attrs = self._validate(join.right)
        join_attrs = left_attrs + right_attrs
        self._validate_condition(join.condition, join_attrs)

        return join_attrs

    def _validate_Division(self, div: Division) -> list[Attribute]:  # noqa: N802
        left_attrs = self._validate(div.dividend)
        right_attrs = self._validate(div.divisor)

        return [a for a in left_attrs if not any(a.name == b.name for b in right_attrs)]

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> list[Attribute]:  # noqa: N802
        input_attrs = self._validate(agg.expression)
        for attr in agg.group_by:
            if not any(a.name == attr.name for a in input_attrs):
                self.errors.append(UnknownAttributeError(attr.name))
        for a in agg.aggregations:
            if not any(x.name == a.input.name for x in input_attrs):
                self.errors.append(UnknownAttributeError(a.input.name))

        return [Attribute(a.output) for a in agg.aggregations] + agg.group_by

    def _validate_TopN(self, top: TopN) -> list[Attribute]:  # noqa: N802
        input_attrs = self._validate(top.expression)
        if not any(attr.name == top.attribute.name for attr in input_attrs):
            self.errors.append(UnknownAttributeError(top.attribute.name))

        return input_attrs

    def _validate_condition(self, cond: BooleanExpression, attrs: list[Attribute]) -> None:
        if isinstance(cond, Comparison):
            for side in (cond.left, cond.right):
                if isinstance(side, Attribute):
                    matches = [
                        a
                        for a in attrs
                        if a.name == side.name
                        and (side.relation is None or a.relation == side.relation)
                    ]
                    if not matches:
                        self.errors.append(UnknownAttributeError(side.name))
                    elif len(matches) > 1 and side.relation is None:
                        self.errors.append(
                            AmbiguousAttributeError(
                                side.name, [a.relation for a in matches if a.relation]
                            )
                        )
        elif isinstance(cond, BinaryBooleanExpression):
            self._validate_condition(cond.left, attrs)
            self._validate_condition(cond.right, attrs)
        elif isinstance(cond, NotExpression):
            self._validate_condition(cond.expression, attrs)
