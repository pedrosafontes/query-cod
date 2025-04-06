from .views import ProjectQueryViewSet, QueryViewSet


routes = [
    {'regex': r'queries', 'viewset': QueryViewSet, 'basename': 'queries'},
]

nested_routes = [
    {'regex': r'queries', 'viewset': ProjectQueryViewSet, 'basename': 'project-queries'},
]
