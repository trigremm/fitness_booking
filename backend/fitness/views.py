import logging
from collections import namedtuple
from re import A

from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FitnessHall, FitnessHallAppointments
from .serializers import (
    FitenessHallAppointmentCreateSerializer,
    FitenessHallAppointmentSerializer,
    FitnessHallLoadSerializer,
    FitnessHallSerializer,
)


class FitnessHallListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = FitnessHall.objects.all()
    serializer_class = FitnessHallSerializer


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
        write a django or sql command that will return agregated data for all fitness halls for today by hour and by fiteness_hall
        in the followint format:
        [{"fitness_hall": 1, "hour": 13, "load": 2}, {"fitness_hall": 1, "hour": 14, "load": 3}, {"fitness_hall": 2, "hour": 13, "load": 1}, {"fitness_hall": 2, "hour": 14, "load": 2}]
        """
        SQL_select = """
                SELECT fitness_hall_id, hour(appointment) , count(*), fitness_fitnesshall.name , fitness_fitnesshall.capacity
                FROM fitness_fitnesshallappointments, fitness_fitnesshall
                WHERE date(appointment) = CURRENT_DATE() and fitness_fitnesshall.id = fitness_fitnesshallappointments.fitness_hall_id
                GROUP BY fitness_hall_id, hour(appointment)
                ORDER BY fitness_hall_id, hour(appointment);
            """

        header = [
            "fitness_hall_id",
            "hour",
            "load",
            "name",
            "capacity",
        ]

        with connection.cursor() as cursor:
            cursor.execute(SQL_select)
            nt_result = namedtuple("Result", header)
            data = [nt_result(*row)._asdict() for row in cursor.fetchall()]
        return Response(data=data, status=status.HTTP_200_OK)
