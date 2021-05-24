import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import chat.routing
from chat.authentication.websocket_middleware import TokenAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myChannelTuto.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":
        TokenAuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        ),
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         chat.routing.websocket_urlpatterns
    #     )
    # ),
})
