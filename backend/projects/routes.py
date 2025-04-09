from projects.views import ProjectViewSet


routes = [
    {'regex': r'projects', 'viewset': ProjectViewSet, 'basename': 'projects'},
]
