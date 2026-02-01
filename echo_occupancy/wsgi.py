"""
WSGI config for echo_occupancy project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echo_occupancy.settings')

application = get_wsgi_application()

