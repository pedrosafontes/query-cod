import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'query_cod.settings.production')

application = get_wsgi_application()
