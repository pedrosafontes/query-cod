from django.core import management

from ra_sql_visualisation import celery_app


@celery_app.task  # type: ignore[misc]
def clearsessions() -> None:
    management.call_command('clearsessions')
