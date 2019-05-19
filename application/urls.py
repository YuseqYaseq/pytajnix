from django.conf.urls import url

from . import views
from django.urls import path

app_name = 'application'
urlpatterns = [
    # lecturer panel
    path('lecturer/', views.lecturer_panel, name='lecturer_panel'),
    path('lecturer/<str:lecture_id>', views.lecturer_panel_lecture, name='lecturer_panel_lecture'),

    # user panel
    path('user/', views.user_panel, name='user_panel'),
    path('user/<str:lecture_id>', views.user_panel_lecture, name='user_panel_lecture'),

    # moderator_panel
    path('moderator/', views.mod_panel, name='mod_panel'),
    path('moderator/<str:lecture_id>', views.mod_panel_lecture, name='mod_panel_lecture'),

    #login
    path('login/', views.user_login, name='user_login'),
    
    #register
    path('reg/', views.user_signup, name='user_signup'),
    
    #logout
    path('lout/', views.user_logout, name='user_logout'),
]