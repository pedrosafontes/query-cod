from queries.serializers.execution import (
    QueryExecutionSerializer,
)


def test_query_execution_serializer_valid_data() -> None:
    data = {
        'success': True,
        'results': {
            'columns': ['id', 'name'],
            'rows': [['1', 'Alice'], ['2', 'Bob']],
        },
    }
    serializer = QueryExecutionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    assert serializer.validated_data['success'] is True
    assert len(serializer.validated_data['results']['rows']) == 2
