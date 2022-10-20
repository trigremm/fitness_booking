from django.db import models

from users.models import User


class FitnessHall(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"[{self.id}] {self.name}"


class FitnessHallAppointments(models.Model):
    fitnessHall = models.ForeignKey(FitnessHall, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.DateTimeField()
    has_appointment = models.BooleanField(default=False)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.id}] {self.fitnessHall.name} - {self.user.email} - {self.appointment}"
