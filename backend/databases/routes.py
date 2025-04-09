from .views import DatabaseViewSet


routes = [
    {'regex': r'databases', 'viewset': DatabaseViewSet, 'basename': 'databases'},
]
