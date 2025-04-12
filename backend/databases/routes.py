from common.types import RouteConfig

from .views import DatabaseViewSet


routes: list[RouteConfig] = [
    {'regex': r'databases', 'viewset': DatabaseViewSet, 'basename': 'databases'},
]
