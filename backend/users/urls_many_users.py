from django.urls import path

from users.views import UserListView

urlpatterns = [
    path("list/", UserListView.as_view()),
]
