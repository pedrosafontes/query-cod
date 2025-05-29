from common.types import RouteConfig

from .views import ExerciseViewSet


routes: list[RouteConfig] = [
    {'regex': r'exercises', 'viewset': ExerciseViewSet, 'basename': 'exercises'},
]
