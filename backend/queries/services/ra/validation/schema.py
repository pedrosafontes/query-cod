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


class RASchemaValidator:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.errors: list[RAValidationError] = []

    def validate(self, expr: RAExpression) -> list[RAValidationError]:
        self.errors = []
        self._validate(expr)
        return self.errors

    def _validate(self, expr: RAExpression) -> None:
        method = getattr(self, f'_validate_{type(expr).__name__}', None)
        if not method:
            raise NotImplementedError(f'No validation implemented for {type(expr).__name__}')
        method(expr)

    def _validate_Relation(self, rel: Relation) -> None: # noqa: N802
        if rel.name not in self.schema:
            self.errors.append(UnknownRelationError(rel.name))

    def _validate_Projection(self, proj: Projection) -> None: # noqa: N802
        self._validate(proj.expression)
        input_attrs = self._infer_attributes(proj.expression)
        for attr in proj.attributes:
            matches = [
                a
                for a in input_attrs
                if a.name == attr.name and (attr.relation is None or a.relation == attr.relation)
            ]
            if not matches:
                self.errors.append(UnknownAttributeError(attr.name))

    def _validate_Selection(self, sel: Selection) -> None: # noqa: N802
        self._validate(sel.expression)
        input_attrs = self._infer_attributes(sel.expression)
        self._validate_condition(sel.condition, input_attrs)

    def _validate_SetOperation(self, op: SetOperation) -> None: # noqa: N802
        self._validate(op.left)
        self._validate(op.right)

    def _validate_Join(self, join: Join) -> None: # noqa: N802
        self._validate(join.left)
        self._validate(join.right)

    def _validate_ThetaJoin(self, join: ThetaJoin) -> None: # noqa: N802
        self._validate(join.left)
        self._validate(join.right)
        attrs = self._infer_attributes(join)
        self._validate_condition(join.condition, attrs)

    def _validate_Division(self, div: Division) -> None: # noqa: N802
        self._validate(div.dividend)
        self._validate(div.divisor)

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> None: # noqa: N802
        self._validate(agg.expression)
        input_attrs = self._infer_attributes(agg.expression)
        for attr in agg.group_by:
            if not any(a.name == attr.name for a in input_attrs):
                self.errors.append(UnknownAttributeError(attr.name))
        for a in agg.aggregations:
            if not any(x.name == a.input.name for x in input_attrs):
                self.errors.append(UnknownAttributeError(a.input.name))

    def _validate_TopN(self, top: TopN) -> None: # noqa: N802
        self._validate(top.expression)
        input_attrs = self._infer_attributes(top.expression)
        if not any(attr.name == top.attribute.name for attr in input_attrs):
            self.errors.append(UnknownAttributeError(top.attribute.name))

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

    def _infer_attributes(self, expr: RAExpression) -> list[Attribute]:
        if isinstance(expr, Relation):
            return [Attribute(name, relation=expr.name) for name in self.schema.get(expr.name, [])]
        if isinstance(expr, Projection):
            return expr.attributes
        if isinstance(expr, Selection):
            return self._infer_attributes(expr.expression)
        if isinstance(expr, SetOperation):
            return self._infer_attributes(expr.left)
        if isinstance(expr, Join) or isinstance(expr, ThetaJoin):
            return self._infer_attributes(expr.left) + self._infer_attributes(expr.right)
        if isinstance(expr, GroupedAggregation):
            return [Attribute(a.output) for a in expr.aggregations] + expr.group_by
        if isinstance(expr, TopN):
            return self._infer_attributes(expr.expression)
        if isinstance(expr, Division):
            return self._infer_attributes(expr.dividend)
        return []
