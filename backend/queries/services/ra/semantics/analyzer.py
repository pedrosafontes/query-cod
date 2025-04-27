from collections import defaultdict
from collections.abc import Callable

from databases.types import Schema
from queries.services.types import AttributeSchema, RelationalSchema, merge_common_column
from ra_sql_visualisation.types import DataType

from ..parser.ast import (
    ASTNode,
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
from .types import RelationOutput, TypedAttribute
from .utils import type_of_function, type_of_value


class RASemanticAnalyzer:
    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, expr: RAExpression) -> None:
        self._validate(expr)

    def _validate(self, expr: RAExpression) -> RelationOutput:  # noqa: N802
        method: Callable[[RAExpression], RelationOutput] = getattr(self, f'_validate_{type(expr).__name__}')
        return method(expr)

    def _validate_Relation(self, rel: Relation) -> RelationOutput:  # noqa: N802
        if rel.name not in self.schema:
            raise UndefinedRelationError(rel, rel.name)
        rel_schema = self.schema[rel.name]
        return RelationOutput(
            {rel.name: rel_schema}, [TypedAttribute(attr, t) for attr, t in rel_schema.items()]
        )

    def _validate_Projection(self, proj: Projection) -> RelationOutput:  # noqa: N802
        input_ = self._validate(proj.expression)
        output_schema: RelationalSchema = defaultdict(AttributeSchema)
        output_attrs = []
        for attr in proj.attributes:
            t = self._resolve_attribute(attr, input_.schema)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))
        return RelationOutput(output_schema, output_attrs)

    def _validate_Selection(self, sel: Selection) -> RelationOutput:  # noqa: N802
        input_ = self._validate(sel.expression)
        self._validate_condition(sel.condition, input_.schema)
        return input_

    def _validate_SetOperation(self, op: SetOperation) -> RelationOutput:  # noqa: N802
        left = self._validate(op.left)
        right = self._validate(op.right)
        match op.operator:
            case SetOperator.CARTESIAN:
                merged_schema = self._merge_schemas(op, left.schema, right.schema)
                return RelationOutput(merged_schema, left.attrs + right.attrs)
            case _:
                # Check if the schemas are union compatible
                if not all(a == b for a, b in zip(left.attrs, right.attrs, strict=False)):
                    raise UnionCompatibilityError(op, op.operator, left.attrs, right.attrs)
                flat_schema = self._flatten(op, left.schema)
                return RelationOutput(flat_schema, left.attrs)

    def _validate_Join(self, join: Join) -> RelationOutput:  # noqa: N802
        left = self._validate(join.left)
        right = self._validate(join.right)
        merged_schema = self._merge_schemas(join, left.schema, right.schema)

        left_names = {attr.name for attr in left.attrs}
        right_names = {attr.name for attr in right.attrs}
        shared_names = left_names & right_names
        shared_attrs = []

        for name in shared_names:
            left_type = self._resolve_attribute(Attribute(name), left.schema, source=join)
            right_type = self._resolve_attribute(Attribute(name), right.schema, source=join)
            if left_type != right_type:
                raise JoinAttributeTypeMismatchError(join, name, left_type, right_type)
            merge_common_column(merged_schema, name)
            shared_attrs.append(TypedAttribute(name, DataType.dominant([left_type, right_type])))

        left_output_attrs = [attr for attr in left.attrs if attr.name not in shared_names]
        right_output_attrs = [attr for attr in right.attrs if attr.name not in shared_names]
        return RelationOutput(merged_schema, left_output_attrs + shared_attrs + right_output_attrs)

    def _validate_ThetaJoin(self, join: ThetaJoin) -> RelationOutput:  # noqa: N802
        left = self._validate(join.left)
        right = self._validate(join.right)
        merged_schema = self._merge_schemas(join, left.schema, right.schema)
        self._validate_condition(join.condition, merged_schema)
        return RelationOutput(merged_schema, left.attrs + right.attrs)

    def _validate_Division(self, div: Division) -> RelationOutput:  # noqa: N802
        dividend = self._validate(div.dividend)
        divisor = self._validate(div.divisor)

        [(_, dividend_schema)] = self._flatten(div.dividend, dividend.schema).items()
        [(_, divisor_schema)] = self._flatten(div.divisor, divisor.schema).items()

        for name, t in divisor_schema.items():
            if name not in dividend_schema:
                raise DivisionSchemaMismatchError(div, dividend_schema, divisor_schema)
            if dividend_schema[name] != t:
                raise DivisionTypeMismatchError(div, name, dividend_schema[name], t)

        output_attrs = [attr for attr in dividend.attrs if attr not in divisor.attrs]
        output_schema: RelationalSchema = {None: {attr.name: attr.data_type for attr in output_attrs}}
        return RelationOutput(output_schema, output_attrs)

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> RelationOutput:  # noqa: N802
        input_ = self._validate(agg.expression)
        output_schema: RelationalSchema = defaultdict(AttributeSchema)
        output_attrs = []

        for attr in agg.group_by:
            t = self._resolve_attribute(attr, input_.schema)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))

        for a in agg.aggregations:
            t = self._resolve_attribute(a.input, input_.schema)
            input_types, output_type = type_of_function(a.aggregation_function, t)
            if t not in input_types:
                raise InvalidFunctionArgumentError(
                    source=agg,
                    function=a.aggregation_function,
                    expected=input_types,
                    actual=t,
                )
            output_schema[None][a.output] = output_type
            output_attrs.append(TypedAttribute(a.output, t))

        return RelationOutput(output_schema, output_attrs)

    def _validate_TopN(self, top: TopN) -> RelationOutput:  # noqa: N802
        input_ = self._validate(top.expression)
        self._resolve_attribute(top.attribute, input_.schema)
        return input_

    def _validate_condition(self, cond: BooleanExpression, schema: RelationalSchema) -> None:
        match cond:
            case Attribute():
                t = self._resolve_attribute(cond, schema)
                if t != DataType.BOOLEAN:
                    raise TypeMismatchError(cond, DataType.BOOLEAN, t)
            case Comparison():
                self._validate_comparison(cond, schema)
            case BinaryBooleanExpression(left=left, right=right):
                self._validate_condition(left, schema)
                self._validate_condition(right, schema)
            case NotExpression(expression=inner):
                self._validate_condition(inner, schema)

    def _validate_comparison(self, cond: Comparison, schema: RelationalSchema) -> None:
        types = []
        for side in (cond.left, cond.right):
            if isinstance(side, Attribute):
                types.append(self._resolve_attribute(side, schema))
            else:
                types.append(type_of_value(side))

        left_type, right_type = types
        if not left_type.is_comparable_with(right_type):
            raise TypeMismatchError(cond, left_type, right_type)

    def _resolve_attribute(
        self, attr: Attribute, schema: RelationalSchema, source: ASTNode | None = None
    ) -> DataType:
        if source is None:
            source = attr
        if attr.relation:
            return self._resolve_qualified(source, attr, schema)
        else:
            return self._resolve_unqualified(source, attr, schema)

    def _resolve_qualified(
        self, source: ASTNode, attr: Attribute, schema: RelationalSchema
    ) -> DataType:
        if attr.relation not in schema:
            raise UndefinedRelationError(source, str(attr.relation))
        if attr.name not in schema[attr.relation]:
            raise UndefinedAttributeError(source, attr)
        return schema[attr.relation][attr.name]

    def _resolve_unqualified(
        self, source: ASTNode, attr: Attribute, schema: RelationalSchema
    ) -> DataType:
        matches = [
            (table, schema[attr.name]) for table, schema in schema.items() if attr.name in schema
        ]
        if not matches:
            raise UndefinedAttributeError(source, attr)
        # Check for ambiguous column
        if len(matches) > 1:
            raise AmbiguousAttributeError(
                source, attr.name, [table for table, _ in matches if table]
            )
        # There is only one match
        [(_, t)] = matches
        return t

    def _flatten(self, source: ASTNode, schema: RelationalSchema) -> RelationalSchema:
        flat: AttributeSchema = {}
        for attributes in schema.values():
            for attr, t in attributes.items():
                if attr in flat and flat[attr] != t:
                    raise TypeMismatchError(source, flat[attr], t)
                flat[attr] = t
        return {None: flat}

    def _merge_schemas(
        self, operator: Join | ThetaJoin | SetOperation, left: RelationalSchema, right: RelationalSchema
    ) -> RelationalSchema:
        merged: RelationalSchema = dict(left)
        for rel, attrs in right.items():
            if rel in merged:
                for attr, t in attrs.items():
                    if attr in merged[rel] and merged[rel][attr] != t:
                        raise JoinAttributeTypeMismatchError(operator, attr, merged[rel][attr], t)
                    merged[rel][attr] = t
            else:
                merged[rel] = dict(attrs)
        return merged
