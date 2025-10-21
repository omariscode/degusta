"""
ASGI config for degusta project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'degusta.settings')

try:
	from channels.routing import ProtocolTypeRouter, URLRouter
	from channels.auth import AuthMiddlewareStack
	from django.core.asgi import get_asgi_application
	from api import routing as api_routing

	django_asgi_app = get_asgi_application()

	application = ProtocolTypeRouter({
		'http': django_asgi_app,
		'websocket': AuthMiddlewareStack(
			URLRouter(api_routing.websocket_urlpatterns)
		),
	})
except Exception:
	# Fallback to Django ASGI if channels not installed
	from django.core.asgi import get_asgi_application
	application = get_asgi_application()
