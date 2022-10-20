from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import FitnessHallAppointments
from .serializers import (
    FitnessHallLoadSerializer,
    FitenessHallAppointmentSerializer,
    FitenessHallAppointmentCreateSerializer,
)
from django.utils import timezone


class FitnessHallAppointmenCreateApiView(CreateAPIView):
    """user made appointment himself"""

    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentCreateSerializer


class FitnessHallAppointmenDestroyApiView(DestroyAPIView):
    """user cancel appointment himself"""

    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentCreateSerializer


class FitnessHallAppointmentAddVisitorCreateAPIView(CreateAPIView):
    """staff adds appointment"""

    model = FitnessHallAppointments
    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentSerializer


class FitnessHallAppointmenRetrieveApiView(RetrieveAPIView):
    model = FitnessHallAppointments
    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentSerializer

    def get_object(self):
        return get_object_or_404(self.model, user=self.request.user, appointment__date=timezone.now().date())


class FitnessHallLoadListAPIView(ListAPIView):
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitnessHallLoadSerializer
    permission_classes = (IsAuthenticated,)
