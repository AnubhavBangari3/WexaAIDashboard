from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


@database_sync_to_async
def get_user_from_token(token):
    if not token:
        return AnonymousUser()

    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated_token)
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        scope["user"] = await get_user_from_token(token)

        return await super().__call__(scope, receive, send)


class LiveDashboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")

        if not user or not user.is_authenticated or not user.organization_id:
            await self.close(code=4001)
            return

        self.organization_id = user.organization_id
        self.group_name = f"org_{self.organization_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send_json(
            {
                "type": "connection",
                "status": "connected",
                "message": "Live dashboard connected",
                "organization_id": self.organization_id,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        if event_type == "ping":
            await self.send_json({"type": "pong"})

    async def live_event(self, event):
        await self.send_json(event["payload"])

    async def live_alert(self, event):
        await self.send_json(event["payload"])

    async def dashboard_refresh(self, event):
        await self.send_json(event["payload"])