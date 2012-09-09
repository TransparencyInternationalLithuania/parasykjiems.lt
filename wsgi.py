import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parasykjiems.settings")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
