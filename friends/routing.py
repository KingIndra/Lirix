# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/user/notifications/", consumers.NotificationConsumer.as_asgi()),
    path("ws/user/chat/<str:username>/", consumers.PersonalChatConsumer.as_asgi()),
]
