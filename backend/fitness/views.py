import logging
from re import A

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FitnessHallAppointments
from .serializers import (
    FitenessHallAppointmentCreateSerializer,
    FitenessHallAppointmentSerializer,
    FitnessHallLoadSerializer,
)


class FitnessHallAppointmenCreateApiView(CreateAPIView):
    """user made appointment himself"""

    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentCreateSerializer

    def post(self, request, *args, **kwargs):
        request.data.update({"user": request.user.id})
        return super().post(request, *args, **kwargs)


class FitnessHallAppointmenDestroyApiView(DestroyAPIView):
    """user cancel appointment himself"""

    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # TODO put to serializer validators
        if instance.user != request.user:
            return Response(
                data="user appointment is not found",
                status=status.HTTP_403_FORBIDDEN,
            )
        if instance.appointment < timezone.now():
            return Response(
                data="appointment time is passed",
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FitnessHallAppointmentAddVisitorCreateAPIView(CreateAPIView):
    """staff adds appointment"""

    model = FitnessHallAppointments
    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_staff is False:
            return Response(data="user is not staff", status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class FitnessHallAppointmenListApiView(ListAPIView):
    model = FitnessHallAppointments
    permission_classes = (IsAuthenticated,)
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitenessHallAppointmentSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, appointment__date=timezone.now().date())


class FitnessHallLoadListAPIView(ListAPIView):
    queryset = FitnessHallAppointments.objects.all()
    serializer_class = FitnessHallLoadSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        """
        get load for all fitness halls for today by hour and by fiteness_hall
        """

        """
        SELECT CAST(t_date_time_issued AS DATE), DATEPART(hour, t_date_time_issued), t_street_name, count(t_reference) 
        FROM tickets 
        WHERE t_date_time_issued BETWEEN '03/06/2015' AND '03/07/2015' 
        AND t_street_name LIKE'%airport%'
        GROUP BY t_street_name, t_reference, CAST(t_date_time_issued AS DATE), DATEPART(hour, t_date_time_issued)
        ORDER BY t_date_time_issued
        """
        queryset = self.get_queryset().filter(appointment__date=timezone.now().date())
        queryset = FitnessHallAppointments.objects.filter(appointment__date=timezone.now().date())

        return super().list(request, *args, **kwargs)
