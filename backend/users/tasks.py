from django.core import management

from query_cod import celery_app


@celery_app.task  # type: ignore[misc]
def clearsessions() -> None:
    management.call_command('clearsessions')
