from common.types import RouteConfig

from .views import AttemptViewSet, ExerciseViewSet


routes: list[RouteConfig] = [
    {'regex': r'exercises', 'viewset': ExerciseViewSet, 'basename': 'exercises'},
    {'regex': r'attempts', 'viewset': AttemptViewSet, 'basename': 'attempts'},
]
