from common.types import RouteConfig

from .views import ProjectQueryViewSet, QueryViewSet


routes: list[RouteConfig] = [
    {'regex': r'queries', 'viewset': QueryViewSet, 'basename': 'queries'},
]

nested_routes: list[RouteConfig] = [
    {'regex': r'queries', 'viewset': ProjectQueryViewSet, 'basename': 'project-queries'},
]
