from collections import defaultdict
from collections.abc import Callable

from databases.types import Schema
from queries.services.types import ProjectionSchema, ResultSchema, merge_common_column
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
from .types import Output, TypedAttribute
from .utils import type_of_function, type_of_value


class RASemanticAnalyzer:
    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, expr: RAExpression) -> None:
        self._validate(expr)

    def _validate(self, expr: RAExpression) -> Output:
        method: Callable[[RAExpression], Output] = getattr(self, f'_validate_{type(expr).__name__}')
        return method(expr)

    def _validate_Relation(self, rel: Relation) -> Output:  # noqa: N802
        if rel.name not in self.schema:
            raise UndefinedRelationError(rel, rel.name)
        rel_schema = self.schema[rel.name]
        return {rel.name: rel_schema}, [TypedAttribute(attr, t) for attr, t in rel_schema.items()]

    def _validate_Projection(self, proj: Projection) -> Output:  # noqa: N802
        input_schema, _ = self._validate(proj.expression)
        output_schema: ResultSchema = defaultdict(ProjectionSchema)
        output_attrs = []

        for attr in proj.attributes:
            t = self._resolve_attribute(attr, input_schema)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))
        return output_schema, output_attrs

    def _validate_Selection(self, sel: Selection) -> Output:  # noqa: N802
        input_schema, input_attrs = self._validate(sel.expression)
        self._validate_condition(sel.condition, input_schema)
        return input_schema, input_attrs

    def _validate_SetOperation(self, op: SetOperation) -> Output:  # noqa: N802
        left_schema, left_attrs = self._validate(op.left)
        right_schema, right_attrs = self._validate(op.right)

        match op.operator:
            case SetOperator.CARTESIAN:
                return self._merge_schemas(op, left_schema, right_schema), left_attrs + right_attrs
            case _:
                union_compatible = all(
                    a == b
                    for a, b in zip(
                        left_attrs,
                        right_attrs,
                        strict=False,
                    )
                )

                if not union_compatible:
                    raise UnionCompatibilityError(op, op.operator, left_attrs, right_attrs)
                return self._flatten(op, left_schema), left_attrs

    def _validate_Join(self, join: Join) -> Output:  # noqa: N802
        left_schema, left_attrs = self._validate(join.left)
        right_schema, right_attrs = self._validate(join.right)
        merged_schema = self._merge_schemas(join, left_schema, right_schema)

        left_names = [attr.name for attr in left_attrs]
        right_names = [attr.name for attr in right_attrs]
        shared_names = set(left_names) & set(right_names)
        shared_attrs = []
        # All common columns must be comparable
        for name in shared_names:
            left_type = self._resolve_attribute(Attribute(name), left_schema, source=join)
            right_type = self._resolve_attribute(Attribute(name), right_schema, source=join)
            if left_type != right_type:
                raise JoinAttributeTypeMismatchError(join, name, left_type, right_type)
            merge_common_column(merged_schema, name)
            shared_attrs.append(TypedAttribute(name, DataType.dominant([left_type, right_type])))

        left_attrs = [attr for attr in left_attrs if attr.name not in shared_names]
        right_attrs = [attr for attr in right_attrs if attr.name not in shared_names]
        return merged_schema, left_attrs + shared_attrs + right_attrs

    def _validate_ThetaJoin(self, join: ThetaJoin) -> Output:  # noqa: N802
        left_schema, left_attrs = self._validate(join.left)
        right_schema, right_attrs = self._validate(join.right)
        join_schema = self._merge_schemas(join, left_schema, right_schema)
        self._validate_condition(join.condition, join_schema)
        return join_schema, left_attrs + right_attrs

    def _validate_Division(self, div: Division) -> Output:  # noqa: N802
        input_dividend_schema, dividend_attrs = self._validate(div.dividend)
        input_divisor_schema, divisor_attrs = self._validate(div.divisor)

        [(_, dividend_schema)] = self._flatten(div.dividend, input_dividend_schema).items()
        [(_, divisor_schema)] = self._flatten(div.divisor, input_divisor_schema).items()

        for name, t in divisor_schema.items():
            if name not in dividend_schema:
                raise DivisionSchemaMismatchError(div, dividend_schema, divisor_schema)
            if dividend_schema[name] != t:
                raise DivisionTypeMismatchError(div, name, dividend_schema[name], t)

        output_attrs = [attr for attr in dividend_attrs if attr not in divisor_attrs]
        output_schema = dict([(attr.name, attr.data_type) for attr in output_attrs])
        return {None: output_schema}, output_attrs

    def _validate_GroupedAggregation(self, agg: GroupedAggregation) -> Output:  # noqa: N802
        input_schema, _ = self._validate(agg.expression)
        output_schema: ResultSchema = defaultdict(ProjectionSchema)
        output_attrs = []

        # Validate group by attributes
        for attr in agg.group_by:
            t = self._resolve_attribute(attr, input_schema)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))

        # Validate aggregation functions and their arguments
        for a in agg.aggregations:
            t = self._resolve_attribute(a.input, input_schema)
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

        return output_schema, output_attrs

    def _validate_TopN(self, top: TopN) -> Output:  # noqa: N802
        input_schema, input_attrs = self._validate(top.expression)
        self._resolve_attribute(top.attribute, input_schema)
        return input_schema, input_attrs

    def _validate_condition(self, cond: BooleanExpression, schema: ResultSchema) -> None:
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

    def _validate_comparison(self, cond: Comparison, schema: ResultSchema) -> None:
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
        self, attr: Attribute, schema: ResultSchema, source: ASTNode | None = None
    ) -> DataType:
        if source is None:
            source = attr
        if attr.relation:
            return self._resolve_qualified(source, attr, schema)
        else:
            return self._resolve_unqualified(source, attr, schema)

    def _resolve_qualified(
        self, source: ASTNode, attr: Attribute, schema: ResultSchema
    ) -> DataType:
        if attr.relation not in schema:
            raise UndefinedRelationError(source, str(attr.relation))
        if attr.name not in schema[attr.relation]:
            raise UndefinedAttributeError(source, attr)
        return schema[attr.relation][attr.name]

    def _resolve_unqualified(
        self, source: ASTNode, attr: Attribute, schema: ResultSchema
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

    def _flatten(self, node: ASTNode, schema: ResultSchema) -> ResultSchema:
        flat: ProjectionSchema = {}
        for attributes in schema.values():
            for attr, t in attributes.items():
                if attr in flat and not flat[attr] != t:
                    raise TypeMismatchError(node, flat[attr], t)
                elif attr not in flat:
                    flat[attr] = t
        return {None: flat}

    def _merge_schemas(
        self, operator: Join | ThetaJoin | SetOperation, left: ResultSchema, right: ResultSchema
    ) -> ResultSchema:
        merged: ResultSchema = dict(left)
        for rel, attrs in right.items():
            if rel in merged:
                for attr, t in attrs.items():
                    if attr in merged[rel] and not merged[rel][attr] != t:
                        raise JoinAttributeTypeMismatchError(operator, attr, merged[rel][attr], t)
                    else:
                        merged[rel][attr] = t
            else:
                merged[rel] = dict(attrs)
        return merged
