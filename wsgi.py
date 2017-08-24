import os
import sys

import django.core.wsgi
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parasykjiems.settings")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
