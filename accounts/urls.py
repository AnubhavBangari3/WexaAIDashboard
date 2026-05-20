from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SignupView,
    LoginView,
    MeView,
    InviteUserView,
    OrganizationUsersView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("invite/", InviteUserView.as_view(), name="invite_user"),
    path("users/", OrganizationUsersView.as_view(), name="organization_users"),
]