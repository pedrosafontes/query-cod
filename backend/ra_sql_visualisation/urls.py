from django.contrib import admin
from django.urls import include, path

import django_js_reverse.views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from users.routes import routes as users_routes
from projects.routes import routes as projects_routes
from queries.routes import routes as queries_routes, nested_routes as project_queries_routes
from rest_framework_nested.routers import NestedDefaultRouter

router = DefaultRouter()

routes = users_routes + projects_routes + queries_routes
for route in routes:
    router.register(route['regex'], route['viewset'], basename=route['basename'])

projects_router = NestedDefaultRouter(router, r'projects', lookup='project')

for route in project_queries_routes:
    projects_router.register(
        route['regex'],
        route['viewset'],
        basename=route['basename'],
    )

urlpatterns = [
    path('', include('common.urls'), name='common'),
    path('admin/', admin.site.urls, name='admin'),
    path('admin/defender/', include('defender.urls')),
    path('jsreverse/', django_js_reverse.views.urls_js, name='js_reverse'),
    path('api/', include(router.urls), name='api'),
    path('api/', include(projects_router.urls)),
    # drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]
