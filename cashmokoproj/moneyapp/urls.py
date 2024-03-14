from . import views
from django.contrib import admin
from django.urls import include, path

# urlpatterns = [
#     path('', views.home, name="home"),
#     path('login', views.login, name="login"),
#     path('mainpage', views.mainpage, name="mainpage")
# ]
urlpatterns = [
    path("", views.home, name="home"),
    path("login_user/", views.login_user, name="login"),
    path("mainpage/", views.mainpage, name="mainpage"),
    path("userbalances/", views.userbalances, name="userbalances"),
    path("useripon/", views.useripon, name="useripon"),
    path("userprofile/", views.userprofile, name="userprofile"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_user, name="logout"),
    path("accounts/login/", views.login_user, name="login"),
]
