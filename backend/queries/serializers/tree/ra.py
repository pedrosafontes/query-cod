from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from queries.services.ra.tree.types import RATree
from rest_framework import serializers


class RATreeSerializer(serializers.Serializer[RATree]):
    id = serializers.IntegerField()
    label = serializers.CharField()  # type: ignore[assignment]
    sub_trees = serializers.SerializerMethodField()

    @extend_schema_field(
        lazy_serializer('queries.serializers.tree.RATreeSerializer')(many=True, required=False)
    )
    def get_sub_trees(self, obj: RATree) -> list[RATree] | None:
        return obj.get('sub_trees')
