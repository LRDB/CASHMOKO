
from . import views
from django.contrib import admin
from django.urls import include, path

# urlpatterns = [
#     path('', views.home, name="home"),
#     path('login', views.login, name="login"),
#     path('mainpage', views.mainpage, name="mainpage")
# ]
urlpatterns = [
    path('', views.home, name='home'),
    path('login_user/', views.login_user, name='login'),
    path('mainpage/', views.mainpage, name='mainpage'),
]
