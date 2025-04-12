from typing import TypedDict

from rest_framework.viewsets import ViewSetMixin


class RouteConfig(TypedDict):
    regex: str
    viewset: type[ViewSetMixin]
    basename: str
