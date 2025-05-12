from enum import Enum

from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from queries.services.ra.tree.types import RATree
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


class RATreeSerializer(serializers.Serializer[RATree]):
    id = serializers.IntegerField()
    label = serializers.CharField()  # type: ignore[assignment]
    sub_trees = serializers.SerializerMethodField()

    @extend_schema_field(
        lazy_serializer('queries.serializers.RATreeSerializer')(many=True, required=False)
    )
    def get_sub_trees(self, obj: RATree) -> list[RATree] | None:
        return obj.get('sub_trees')


class SQLNodeType(str, Enum):
    TABLE = 'table'
    ALIAS = 'alias'
    JOIN = 'join'
    SELECT = 'select'
    WHERE = 'where'
    GROUP_BY = 'group_by'
    HAVING = 'having'
    ORDER_BY = 'order_by'
    SET_OP = 'set_op'


class SQLTreeSerializer(serializers.Serializer[SQLTree]):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=[node_type.value for node_type in SQLNodeType], required=True
    )
    children = serializers.SerializerMethodField()

    # Type-specific fields
    name = serializers.SerializerMethodField(required=False)
    alias = serializers.SerializerMethodField(required=False)
    method = serializers.SerializerMethodField(required=False)
    condition = serializers.SerializerMethodField(required=False)
    using = serializers.SerializerMethodField(required=False)
    columns = serializers.SerializerMethodField(required=False)
    keys = serializers.SerializerMethodField(required=False)
    operator = serializers.SerializerMethodField(required=False)

    def get_type(self, obj: SQLTree) -> SQLNodeType:
        match obj:
            case TableNode():
                return SQLNodeType.TABLE
            case AliasNode():
                return SQLNodeType.ALIAS
            case JoinNode():
                return SQLNodeType.JOIN
            case SelectNode():
                return SQLNodeType.SELECT
            case WhereNode():
                return SQLNodeType.WHERE
            case GroupByNode():
                return SQLNodeType.GROUP_BY
            case HavingNode():
                return SQLNodeType.HAVING
            case OrderByNode():
                return SQLNodeType.ORDER_BY
            case SetOpNode():
                return SQLNodeType.SET_OP

    @extend_schema_field(
        lazy_serializer('queries.serializers.SQLTreeSerializer')(many=True, required=False)
    )
    def get_children(self, obj: SQLTree) -> list[SQLTree] | None:
        return obj.children

    def get_name(self, obj: SQLTree) -> str | None:
        return obj.name if hasattr(obj, 'name') else None

    def get_alias(self, obj: SQLTree) -> str | None:
        return obj.alias if hasattr(obj, 'alias') else None

    def get_method(self, obj: SQLTree) -> str | None:
        return obj.method if hasattr(obj, 'method') else None

    def get_condition(self, obj: SQLTree) -> str | None:
        return obj.condition if hasattr(obj, 'condition') else None

    def get_using(self, obj: SQLTree) -> list[str] | None:
        return obj.using if hasattr(obj, 'using') else None

    def get_columns(self, obj: SQLTree) -> list[str] | None:
        return obj.columns if hasattr(obj, 'columns') else None

    def get_keys(self, obj: SQLTree) -> list[str] | None:
        return obj.keys if hasattr(obj, 'keys') else None

    def get_operator(self, obj: SQLTree) -> str | None:
        return obj.operator if hasattr(obj, 'operator') else None
