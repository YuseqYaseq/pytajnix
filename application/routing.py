# application/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/application/lecturer/(?P<lecture_name>[^/]+)/$', consumers.LecturerConsumer),
    url(r'^ws/application/moderator/(?P<lecture_name>[^/]+)/$', consumers.ModeratorConsumer),
    url(r'^ws/application/user/(?P<lecture_name>[^/]+)/$', consumers.UserConsumer),
]