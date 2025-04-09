from queries.serializers import (
    QueryErrorSerializer,
    QueryExecutionSerializer,
    QuerySerializer,
)


def test_query_serializer_allows_blank_text():
    data = {
        "name": "Example Query",
        "text": "",
    }
    serializer = QuerySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    assert serializer.validated_data["text"] == ""


def test_query_serializer_requires_text_field():
    data = {
        "name": "Missing text",
    }
    serializer = QuerySerializer(data=data)
    assert not serializer.is_valid()
    assert "text" in serializer.errors


def test_query_execution_serializer_valid_data():
    data = {
        "success": True,
        "results": {
            "columns": ["id", "name"],
            "rows": [["1", "Alice"], ["2", "Bob"]],
        }
    }
    serializer = QueryExecutionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    assert serializer.validated_data["success"] is True
    assert len(serializer.validated_data["results"]["rows"]) == 2


def test_query_error_serializer_rejects_missing_fields():
    serializer = QueryErrorSerializer(data={"message": "Oops"})
    assert not serializer.is_valid()
    assert "line" in serializer.errors