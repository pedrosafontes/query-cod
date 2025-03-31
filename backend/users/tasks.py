from django.core import management

from ra_sql_visualisation import celery_app


@celery_app.task
def clearsessions():
    management.call_command("clearsessions")
