from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication

backend = JWTAuthentication()

@database_sync_to_async
def get_user(validated_token):
    try:
        return backend.get_user(validated_token)
    except:
        return


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        token = backend.get_validated_token(scope['query_string'].decode()[6:])
        scope['user'] = await get_user(token)

        return await self.app(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: JwtAuthMiddleware(inner)
