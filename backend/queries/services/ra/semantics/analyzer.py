from functools import singledispatchmethod

from queries.services.types import RelationalSchema, flatten
from ra_sql_visualisation.types import DataType

from ..ast import (
    ASTNode,
    Attribute,
    BinaryBooleanExpression,
    BinaryOperation,
    BooleanExpression,
    Comparison,
    Division,
    GroupedAggregation,
    Join,
    Not,
    Projection,
    RAQuery,
    Relation,
    Rename,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
    UnaryOperation,
)
from ..inference import type_of_function, type_of_value
from ..scope.schema import SchemaInferrer
from ..scope.types import Match, RelationOutput
from .errors import (
    AmbiguousAttributeReferenceError,
    AttributeNotFoundError,
    DivisionAttributeTypeMismatchError,
    DivisionSchemaCompatibilityError,
    InvalidFunctionArgumentError,
    JoinAttributeTypeMismatchError,
    RelationNotFoundError,
    TypeMismatchError,
    UnionCompatibilityError,
)


class RASemanticAnalyzer:
    def __init__(self, schema: RelationalSchema):
        self.schema = schema
        self._schema_inferrer = SchemaInferrer(schema)

    def validate(self, query: RAQuery) -> None:
        if isinstance(query, UnaryOperation):
            self._validate(query.subquery)
        elif isinstance(query, BinaryOperation):
            self._validate(query.left)
            self._validate(query.right)
        return self._validate(query)

    @singledispatchmethod
    def _validate(self, query: RAQuery) -> None:
        raise NotImplementedError(f'No validator for {type(query).__name__}')

    @_validate.register
    def _(self, rel: Relation) -> None:
        if rel.name not in self.schema:
            raise RelationNotFoundError(rel, rel.name)

    @_validate.register
    def _(self, proj: Projection) -> None:
        input_ = self._schema_inferrer.infer(proj.subquery)
        for attr in proj.attributes:
            self._validate_attribute(attr, [input_])

    @_validate.register
    def _(self, sel: Selection) -> None:
        input_ = self._schema_inferrer.infer(sel.subquery)
        self._validate_condition(sel.condition, [input_])

    @_validate.register
    def _(self, _: Rename) -> None:
        pass

    @_validate.register
    def _(self, op: SetOperation) -> None:
        left = self._schema_inferrer.infer(op.left)
        right = self._schema_inferrer.infer(op.right)
        if op.operator != SetOperator.CARTESIAN:
            if not all(
                a.data_type == b.data_type for a, b in zip(left.attrs, right.attrs, strict=True)
            ):
                raise UnionCompatibilityError(op, op.operator, left.attrs, right.attrs)

    @_validate.register
    def _(self, join: Join) -> None:
        left = self._schema_inferrer.infer(join.left)
        right = self._schema_inferrer.infer(join.right)

        left_names = {attr.name for attr in left.attrs}
        right_names = {attr.name for attr in right.attrs}
        shared_names = left_names & right_names

        for name in shared_names:
            left_type = self._validate_attribute(Attribute(name), [left], source=join)
            right_type = self._validate_attribute(Attribute(name), [right], source=join)
            if left_type != right_type:
                raise JoinAttributeTypeMismatchError(join, name, left_type, right_type)

    @_validate.register
    def _(self, join: ThetaJoin) -> None:
        left = self._schema_inferrer.infer(join.left)
        right = self._schema_inferrer.infer(join.right)
        self._validate_condition(join.condition, [left, right])

    @_validate.register
    def _(self, div: Division) -> None:
        dividend = self._schema_inferrer.infer(div.dividend)
        divisor = self._schema_inferrer.infer(div.divisor)

        dividend_attrs = flatten(dividend.schema)
        divisor_attrs = flatten(divisor.schema)

        for name, t in divisor_attrs.items():
            if name not in dividend_attrs:
                raise DivisionSchemaCompatibilityError(div, dividend_attrs, divisor_attrs)
            if dividend_attrs[name] != t:
                raise DivisionAttributeTypeMismatchError(div, name, dividend_attrs[name], t)

    @_validate.register
    def _(self, agg: GroupedAggregation) -> None:
        input_ = self._schema_inferrer.infer(agg.subquery)

        for attr in agg.group_by:
            self._validate_attribute(attr, [input_])

        for a in agg.aggregations:
            t = self._validate_attribute(a.input, [input_])
            input_types, _ = type_of_function(a.aggregation_function, t)
            if t not in input_types:
                raise InvalidFunctionArgumentError(
                    source=agg,
                    function=a.aggregation_function,
                    expected=input_types,
                    actual=t,
                )

    @_validate.register
    def _(self, top: TopN) -> None:
        input_ = self._schema_inferrer.infer(top.subquery)
        self._validate_attribute(top.attribute, [input_])

    def _validate_condition(self, cond: BooleanExpression, inputs: list[RelationOutput]) -> None:
        match cond:
            case Attribute():
                t = self._validate_attribute(cond, inputs)
                if t != DataType.BOOLEAN:
                    raise TypeMismatchError(cond, DataType.BOOLEAN, t)
            case Comparison():
                self._validate_comparison(cond, inputs)
            case BinaryBooleanExpression(left=left, right=right):
                self._validate_condition(left, inputs)
                self._validate_condition(right, inputs)
            case Not(expression=inner):
                self._validate_condition(inner, inputs)

    def _validate_comparison(self, cond: Comparison, inputs: list[RelationOutput]) -> None:
        types = []
        for side in (cond.left, cond.right):
            if isinstance(side, Attribute):
                types.append(self._validate_attribute(side, inputs))
            else:
                types.append(type_of_value(side))
        left_type, right_type = types
        if not left_type.is_comparable_with(right_type):
            raise TypeMismatchError(cond, left_type, right_type)

    def _validate_attribute(
        self, attr: Attribute, inputs: list[RelationOutput], source: ASTNode | None = None
    ) -> DataType:
        if source is None:
            source = attr

        # Collect all matches across all inputs
        matches: list[Match] = []
        for input_ in inputs:
            matches.extend(input_.resolve(attr))

        if not matches:
            raise AttributeNotFoundError(source, attr)
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousAttributeReferenceError(source, attr.name, [rel for rel, _ in matches])
        # There is only one match
        [(_, t)] = matches
        return t
