"""
WebSocket routing for events app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/waiting-room/(?P<event_id>[0-9a-f-]+)/$', consumers.WaitingRoomConsumer.as_asgi()),
]
