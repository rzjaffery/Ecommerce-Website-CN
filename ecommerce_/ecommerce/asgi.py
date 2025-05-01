"""
ASGI config for ecommerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
import logging

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set up logging
logger = logging.getLogger('django.channels')
logger.setLevel(logging.DEBUG)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Import the chat URL routing after the Django setup to avoid circular imports
import chat.routing

# Simple debugging middleware
class DebugMiddleware:
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            # Log the connection attempt
            path = scope.get('path', '')
            logger.debug(f"WebSocket connection attempt: {path}")
            logger.debug(f"WebSocket scope: {scope}")
        
        return await self.inner(scope, receive, send)

# Define the ASGI application
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': DebugMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})
