from enum import Enum
from typing import Any

from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field
from queries.services.ra.tree.types import (
    DivisionNode,
    GroupedAggregationNode,
    JoinNode,
    ProjectionNode,
    RATree,
    RelationNode,
    SelectionNode,
    SetOperationNode,
    ThetaJoinNode,
    TopNNode,
)
from rest_framework import serializers

from ..error import QueryErrorSerializer


class RANodeType(str, Enum):
    RELATION = 'Relation'
    PROJECTION = 'Projection'
    SELECTION = 'Selection'
    DIVISION = 'Division'
    SET_OPERATION = 'SetOperation'
    JOIN = 'Join'
    THETA_JOIN = 'ThetaJoin'
    GROUPED_AGGREGATION = 'GroupedAggregation'
    TOP_N = 'TopN'


class RATreeNodeSerializer(serializers.Serializer[RATree]):
    id = serializers.IntegerField()
    children = serializers.SerializerMethodField(required=False)
    ra_node_type = serializers.SerializerMethodField()
    validation_errors = QueryErrorSerializer(many=True)

    @extend_schema_field(
        serializers.ChoiceField(
            choices=[node_type.value for node_type in RANodeType], required=True
        )
    )
    def get_ra_node_type(self, obj: RATree) -> str:
        return obj.__class__.__name__.replace('Node', '')

    @extend_schema_field(
        PolymorphicProxySerializer(
            component_name='RATree',
            serializers=[
                lazy_serializer('RelationNodeSerializer'),
                lazy_serializer('ProjectionNodeSerializer'),
                lazy_serializer('SelectionNodeSerializer'),
                lazy_serializer('DivisionNodeSerializer'),
                lazy_serializer('SetOperationNodeSerializer'),
                lazy_serializer('JoinNodeSerializer'),
                lazy_serializer('ThetaJoinNodeSerializer'),
                lazy_serializer('GroupedAggregationNodeSerializer'),
                lazy_serializer('TopNNodeSerializer'),
            ],
            resource_type_field_name=None,
            many=True,
        )
    )
    def get_children(self, obj: RATree) -> list[dict[str, Any]] | None:
        return [RATreeSerializer(child).data for child in obj.children] if obj.children else None


class RelationNodeSerializer(RATreeNodeSerializer):
    name = serializers.CharField()


class ProjectionNodeSerializer(RATreeNodeSerializer):
    attributes = serializers.ListField(child=serializers.CharField())


class SelectionNodeSerializer(RATreeNodeSerializer):
    condition = serializers.CharField()


class DivisionNodeSerializer(RATreeNodeSerializer):
    pass


class SetOperationNodeSerializer(RATreeNodeSerializer):
    operator = serializers.CharField()


class RAJoinNodeSerializer(RATreeNodeSerializer):
    operator = serializers.CharField()


class ThetaJoinNodeSerializer(RATreeNodeSerializer):
    condition = serializers.CharField()


class GroupedAggregationNodeSerializer(RATreeNodeSerializer):
    group_by = serializers.ListField(child=serializers.CharField())
    aggregations = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )  # (input, function, output)


class TopNNodeSerializer(RATreeNodeSerializer):
    limit = serializers.IntegerField()
    attribute = serializers.CharField()


class RATreeSerializer(serializers.Serializer[RATree]):
    def to_representation(self, obj: RATree) -> dict[str, Any]:
        match obj:
            case RelationNode():
                return RelationNodeSerializer(obj).data
            case ProjectionNode():
                return ProjectionNodeSerializer(obj).data
            case SelectionNode():
                return SelectionNodeSerializer(obj).data
            case DivisionNode():
                return DivisionNodeSerializer(obj).data
            case SetOperationNode():
                return SetOperationNodeSerializer(obj).data
            case JoinNode():
                return RAJoinNodeSerializer(obj).data
            case ThetaJoinNode():
                return ThetaJoinNodeSerializer(obj).data
            case GroupedAggregationNode():
                return GroupedAggregationNodeSerializer(obj).data
            case TopNNode():
                return TopNNodeSerializer(obj).data
            case _:
                raise ValueError(f'Unknown RATree node type: {type(obj)}')


RATreeField = PolymorphicProxySerializer(
    component_name='RATree',
    serializers=[
        RelationNodeSerializer,
        ProjectionNodeSerializer,
        SelectionNodeSerializer,
        DivisionNodeSerializer,
        SetOperationNodeSerializer,
        RAJoinNodeSerializer,
        ThetaJoinNodeSerializer,
        GroupedAggregationNodeSerializer,
        TopNNodeSerializer,
    ],
    resource_type_field_name=None,
    required=False,
)
