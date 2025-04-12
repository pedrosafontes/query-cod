from django.conf import settings
from django.http import HttpRequest


def sentry_dsn(request: HttpRequest) -> dict[str, str]:
    return {'SENTRY_DSN': settings.SENTRY_DSN}  # type: ignore[misc]


def commit_sha(request: HttpRequest) -> dict[str, str]:
    return {'COMMIT_SHA': settings.COMMIT_SHA}  # type: ignore[misc]
