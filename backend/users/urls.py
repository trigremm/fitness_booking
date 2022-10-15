from django.urls import path

from users.views import AnonymousUserViewSet, CurrentUserView, UserProfileAPIView

urlpatterns = [
    path("", CurrentUserView.as_view()),
    path("profile/", UserProfileAPIView.as_view()),
    path("password_change/", AnonymousUserViewSet.as_view({"post": "not_implemented"})),
]
