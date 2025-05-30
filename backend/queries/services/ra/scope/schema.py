from collections import defaultdict
from functools import singledispatchmethod

from queries.services.types import Attributes, RelationalSchema, flatten, merge_common_column
from query_cod.types import DataType

from ..ast import (
    Attribute,
    Division,
    GroupedAggregation,
    Join,
    Projection,
    RAQuery,
    Relation,
    Rename,
    Selection,
    SetOperation,
    SetOperator,
    ThetaJoin,
    TopN,
)
from ..inference import type_of_function
from .types import RelationOutput, TypedAttribute
from .utils import merge_schemas


class SchemaInferrer:
    def __init__(self, schema: RelationalSchema):
        self.schema = schema
        self._cache: dict[int, RelationOutput] = {}

    def infer(self, query: RAQuery) -> RelationOutput:
        key = id(query)
        if key not in self._cache:
            self._cache[key] = self._infer(query)
        return self._cache[key]

    @singledispatchmethod
    def _infer(self, query: RAQuery) -> RelationOutput:
        raise NotImplementedError(f'No inference method for {type(query).__name__}')

    @_infer.register
    def _(self, rel: Relation) -> RelationOutput:
        attributes = self.schema[rel.name]
        return RelationOutput(
            {rel.name: attributes}, [TypedAttribute(attr, t) for attr, t in attributes.items()]
        )

    @_infer.register
    def _(self, proj: Projection) -> RelationOutput:
        input_ = self.infer(proj.subquery)
        output_schema: RelationalSchema = defaultdict(Attributes)
        output_attrs = []
        for attr in proj.attributes:
            [(_, t)] = input_.resolve(attr)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))
        return RelationOutput(output_schema, output_attrs)

    @_infer.register
    def _(self, sel: Selection) -> RelationOutput:
        return self.infer(sel.subquery)

    @_infer.register
    def _(self, rename: Rename) -> RelationOutput:
        input_ = self.infer(rename.subquery)
        renamed_schema: RelationalSchema = {rename.alias: flatten(input_.schema)}
        return RelationOutput(renamed_schema, input_.attrs)

    @_infer.register
    def _(self, op: SetOperation) -> RelationOutput:
        left = self.infer(op.left)
        right = self.infer(op.right)

        if op.operator == SetOperator.CARTESIAN:
            return RelationOutput(
                merge_schemas(left.schema, right.schema), left.attrs + right.attrs
            )
        else:
            # Union-compatible operations
            flat_schema: RelationalSchema = {None: flatten(left.schema)}
            return RelationOutput(flat_schema, left.attrs)

    @_infer.register
    def _(self, join: Join) -> RelationOutput:
        left = self.infer(join.left)
        right = self.infer(join.right)
        merged_schema = merge_schemas(left.schema, right.schema)

        left_names = {attr.name for attr in left.attrs}
        right_names = {attr.name for attr in right.attrs}
        shared_names = left_names & right_names
        shared_attrs = []

        for name in shared_names:
            [(_, left_type)] = left.resolve(Attribute(name))
            [(_, right_type)] = right.resolve(Attribute(name))
            merge_common_column(merged_schema, name)
            shared_attrs.append(TypedAttribute(name, DataType.dominant([left_type, right_type])))

        left_unique = [a for a in left.attrs if a.name not in shared_names]
        right_unique = [a for a in right.attrs if a.name not in shared_names]
        return RelationOutput(merged_schema, left_unique + shared_attrs + right_unique)

    @_infer.register
    def _(self, join: ThetaJoin) -> RelationOutput:
        left = self.infer(join.left)
        right = self.infer(join.right)
        return RelationOutput(merge_schemas(left.schema, right.schema), left.attrs + right.attrs)

    @_infer.register
    def _(self, div: Division) -> RelationOutput:
        dividend = self.infer(div.dividend)
        divisor = self.infer(div.divisor)

        divisor_attrs = flatten(divisor.schema)

        output_attrs = [attr for attr in dividend.attrs if attr.name not in divisor_attrs]
        output_schema: RelationalSchema = {
            None: {attr.name: attr.data_type for attr in output_attrs}
        }
        return RelationOutput(output_schema, output_attrs)

    @_infer.register
    def _(self, agg: GroupedAggregation) -> RelationOutput:
        input_ = self.infer(agg.subquery)
        output_schema: RelationalSchema = defaultdict(Attributes)
        output_attrs = []

        for attr in agg.group_by:
            [(_, t)] = input_.resolve(attr)
            output_schema[attr.relation][attr.name] = t
            output_attrs.append(TypedAttribute(attr.name, t))

        for a in agg.aggregations:
            [(_, t)] = input_.resolve(a.input)
            _, output_type = type_of_function(a.aggregation_function, t)
            output_schema[None][a.output] = output_type
            output_attrs.append(TypedAttribute(a.output, output_type))

        return RelationOutput(output_schema, output_attrs)

    @_infer.register
    def _(self, top: TopN) -> RelationOutput:
        return self.infer(top.subquery)
