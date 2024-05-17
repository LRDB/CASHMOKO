from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("userpage", views.userpage, name="userpage"),
    path("logout_user", views.logout_user, name="logout_user"),
    path("user_balances", views.user_balances, name="user_balances"),
    path("iponchallenge", views.iponchallenge, name="iponchallenge"),
    path("Debit", views.Debit, name="Debit"),
    path("Credit", views.Credit, name="Credit"),
    path("Adjustment", views.Adjustment, name="Adjustment"),
    path("Bank Transfer", views.Bank_Transfer, name="Bank Transfer"),
    path("Transactions", views.Transactions, name="Transactions"),
    path("profile", views.profile, name="profile"),
    path("feedback", views.feedback, name="feedback"),
]
