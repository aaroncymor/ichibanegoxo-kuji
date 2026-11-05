from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(
        r"^ws/kuji-session/(?P<session_id>[\w-]+)/$",
        consumers.KujiSessionConsumer.as_asgi(),
    ),
]
