"""Authentication URLs are kept together for easy discovery."""

from django.urls import path

from accounts.views import (
    LoginView,
    LogoutView,
    PasswordView,
    ProfileView,
    RegisterView,
    SessionView,
)

urlpatterns = [
    path("session/", SessionView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("password/", PasswordView.as_view()),
]
