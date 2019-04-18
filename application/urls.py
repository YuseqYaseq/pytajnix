from . import views
from django.urls import path

app_name='application'
urlpatterns =[
    #main view
    path('', views.home, name='home'),

    #login
    path('login/', views.user_login, name='user_login'),
    
    #register
    path('reg/', views.user_signup, name='user_signup'),
    
    #logout
    path('lout/', views.user_logout, name='user_logout'),
]