from django.contrib import admin
from django.urls import include, path

import django_js_reverse.views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from queries.routes import routes as queries_routes
from rest_framework.routers import DefaultRouter
from users.routes import routes as users_routes


router = DefaultRouter()

routes = users_routes + queries_routes
for route in routes:
    router.register(route['regex'], route['viewset'], basename=route['basename'])

urlpatterns = [
    path('', include('common.urls'), name='common'),
    path('admin/', admin.site.urls, name='admin'),
    path('admin/defender/', include('defender.urls')),
    path('jsreverse/', django_js_reverse.views.urls_js, name='js_reverse'),
    path('api/', include(router.urls), name='api'),
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
