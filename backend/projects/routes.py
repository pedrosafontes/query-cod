from common.types import RouteConfig
from projects.views import ProjectViewSet


routes: list[RouteConfig] = [
    {'regex': r'projects', 'viewset': ProjectViewSet, 'basename': 'projects'},
]
