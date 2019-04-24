# application/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/application/(?P<lecture_name>[^/]+)/$', consumers.LecturerConsumer),
]