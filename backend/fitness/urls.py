from django.urls import path

from .views import (
    FitnessHallAppointmenCreateApiView,
    FitnessHallAppointmenDestroyApiView,
    FitnessHallAppointmenListApiView,
    FitnessHallAppointmentAddVisitorCreateAPIView,
    FitnessHallListAPIView,
    FitnessHallLoadListAPIView,
)

urlpatterns = [
    path("schedule_appointment/", FitnessHallAppointmenCreateApiView.as_view()),
    path("cancel_appointment/<int:pk>", FitnessHallAppointmenDestroyApiView.as_view()),
    path("add_visitor/", FitnessHallAppointmentAddVisitorCreateAPIView.as_view(), name="for staff usage only"),
    path("check_appointment/", FitnessHallAppointmenListApiView.as_view()),
    path("list_halls/", FitnessHallListAPIView.as_view()),
    path("list_load/", FitnessHallLoadListAPIView.as_view()),
]
