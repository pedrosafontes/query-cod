from .views import QueryViewSet


routes = [
    {"regex": r"queries", "viewset": QueryViewSet, "basename": "query"},
]
