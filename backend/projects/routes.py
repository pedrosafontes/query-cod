from common.types import RouteConfig
from projects.views import ProjectQueryViewSet, ProjectViewSet, QueryViewSet


routes: list[RouteConfig] = [
    {'regex': r'projects', 'viewset': ProjectViewSet, 'basename': 'projects'},
    {'regex': r'queries', 'viewset': QueryViewSet, 'basename': 'queries'},
]

nested_routes: list[RouteConfig] = [
    {'regex': r'queries', 'viewset': ProjectQueryViewSet, 'basename': 'project-queries'},
]
