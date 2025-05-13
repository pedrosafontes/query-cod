from typing import Any

from drf_spectacular.utils import extend_schema_field
from queries.models import Query
from queries.serializers.tree.sql import SQLTreeField
from rest_framework import serializers

from .tree import RATreeSerializer, SQLTreeSerializer


class QuerySerializer(serializers.ModelSerializer[Query]):
    sql_tree = serializers.SerializerMethodField(required=False)
    ra_tree = RATreeSerializer(required=False)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'sql_text',
            'ra_text',
            'language',
            'created',
            'modified',
            'validation_errors',
            'sql_tree',
            'ra_tree',
        ]

    @extend_schema_field(SQLTreeField)
    def get_sql_tree(self, obj: Query) -> dict[str, Any] | None:
        if obj.sql_tree is None:
            return None
        return SQLTreeSerializer(obj.sql_tree).data


class QuerySummarySerializer(serializers.ModelSerializer[Query]):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
