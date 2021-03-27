# https://github.com/masnun/django-orm-standalone

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.core import management
management.call_command('makemigrations')
management.call_command('migrate')
