"""
ASGI config for echo_occupancy project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echo_occupancy.settings')

application = get_asgi_application()

