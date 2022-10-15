from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import AnonymousUserViewSet

urlpatterns = [
    path("register/", AnonymousUserViewSet.as_view({"post": "user_registration"})),
    path("activate/", AnonymousUserViewSet.as_view({"get": "user_activation"})),
    path("forgot_password/", AnonymousUserViewSet.as_view({"post": "user_forgot_password"})),
    path("reset_password/", AnonymousUserViewSet.as_view({"post": "user_reset_password"})),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("login/", TokenObtainPairView.as_view(), name="obtain_auth_token_pair"),
]
