
from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/real_time_data/', consumer.RealTimeData.as_asgi()),
    re_path(r'ws/dash_real_time_data/', consumer.DashBoardRealTime.as_asgi()),
]
