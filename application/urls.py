from django.conf.urls import url

from . import views
from django.urls import path

app_name = 'application'
urlpatterns = [
    #main view
    path('', views.home, name='home'),

    # lecturer panel
    path('lecturer/<int:lecture_id>', views.lecturer_panel, name='lecturer_panel'),

    # user panel
    path('user/<int:lecture_id>', views.user_panel, name='user_panel'),

    # moderator_panel
    path('moderator/<int:lecture_id>', views.mod_panel, name='mod_panel'),

    #login
    path('login/', views.user_login, name='user_login'),
    
    #register
    path('reg/', views.user_signup, name='user_signup'),
    
    #logout
    path('lout/', views.user_logout, name='user_logout'),
]