from enum import Enum
from typing import Any

from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field
from queries.services.sql.tree.types import (
    AliasNode,
    GroupByNode,
    HavingNode,
    JoinNode,
    OrderByNode,
    SelectNode,
    SetOpNode,
    SQLTree,
    TableNode,
    WhereNode,
)
from rest_framework import serializers

from ..error import QueryErrorSerializer


class SQLNodeType(str, Enum):
    TABLE = 'Table'
    ALIAS = 'Alias'
    JOIN = 'Join'
    SELECT = 'Select'
    WHERE = 'Where'
    GROUP_BY = 'GroupBy'
    HAVING = 'Having'
    ORDER_BY = 'OrderBy'
    SET_OP = 'SetOp'


class SQLTreeNodeSerializer(serializers.Serializer[SQLTree]):
    id = serializers.IntegerField()
    children = serializers.SerializerMethodField(required=False)
    sql_node_type = serializers.SerializerMethodField()
    validation_errors = QueryErrorSerializer(many=True)

    @extend_schema_field(
        serializers.ChoiceField(
            choices=[node_type.value for node_type in SQLNodeType], required=True
        )
    )
    def get_sql_node_type(self, obj: SQLTree) -> str:
        return obj.__class__.__name__.replace('Node', '')

    @extend_schema_field(
        PolymorphicProxySerializer(
            component_name='SQLTree',
            serializers=[
                lazy_serializer('TableNodeSerializer'),
                lazy_serializer('AliasNodeSerializer'),
                lazy_serializer('SQLJoinNodeSerializer'),
                lazy_serializer('SelectNodeSerializer'),
                lazy_serializer('WhereNodeSerializer'),
                lazy_serializer('GroupByNodeSerializer'),
                lazy_serializer('HavingNodeSerializer'),
                lazy_serializer('OrderByNodeSerializer'),
                lazy_serializer('SetOpNodeSerializer'),
            ],
            resource_type_field_name=None,
            many=True,
        )
    )
    def get_children(self, obj: SQLTree) -> list[dict[str, Any]] | None:
        return [SQLTreeSerializer(child).data for child in obj.children] if obj.children else None


class TableNodeSerializer(SQLTreeNodeSerializer):
    name = serializers.CharField()


class AliasNodeSerializer(SQLTreeNodeSerializer):
    alias = serializers.CharField()


class SQLJoinNodeSerializer(SQLTreeNodeSerializer):
    method = serializers.CharField()
    condition = serializers.CharField(allow_null=True, required=False)
    using = serializers.ListField(child=serializers.CharField(), allow_null=True, required=False)


class SelectNodeSerializer(SQLTreeNodeSerializer):
    columns = serializers.ListField(child=serializers.CharField())


class WhereNodeSerializer(SQLTreeNodeSerializer):
    condition = serializers.CharField()


class GroupByNodeSerializer(SQLTreeNodeSerializer):
    keys = serializers.ListField(child=serializers.CharField())


class HavingNodeSerializer(SQLTreeNodeSerializer):
    condition = serializers.CharField()


class OrderByNodeSerializer(SQLTreeNodeSerializer):
    keys = serializers.ListField(child=serializers.CharField())


class SetOpNodeSerializer(SQLTreeNodeSerializer):
    operator = serializers.CharField()


class SQLTreeSerializer(serializers.Serializer[SQLTree]):
    def to_representation(self, obj: SQLTree) -> dict[str, Any]:
        match obj:
            case TableNode():
                return TableNodeSerializer(obj).data
            case AliasNode():
                return AliasNodeSerializer(obj).data
            case JoinNode():
                return SQLJoinNodeSerializer(obj).data
            case SelectNode():
                return SelectNodeSerializer(obj).data
            case WhereNode():
                return WhereNodeSerializer(obj).data
            case GroupByNode():
                return GroupByNodeSerializer(obj).data
            case HavingNode():
                return HavingNodeSerializer(obj).data
            case OrderByNode():
                return OrderByNodeSerializer(obj).data
            case SetOpNode():
                return SetOpNodeSerializer(obj).data
            case _:
                raise ValueError(f'Unknown SQL tree node type: {type(obj)}')


SQLTreeField = PolymorphicProxySerializer(
    component_name='SQLTree',
    serializers=[
        TableNodeSerializer,
        AliasNodeSerializer,
        SQLJoinNodeSerializer,
        SelectNodeSerializer,
        WhereNodeSerializer,
        GroupByNodeSerializer,
        HavingNodeSerializer,
        OrderByNodeSerializer,
        SetOpNodeSerializer,
    ],
    resource_type_field_name=None,
    required=False,
)
