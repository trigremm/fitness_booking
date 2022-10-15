"""
# how to use signals

from users.signals import user_password_reset_signal

user_password_reset_signal.send(sender=User, user=user)
"""
from django.dispatch import Signal

user_registered_signal = Signal()  # providing_args=["user"]
user_activated_signal = Signal()  # providing_args=["user"]
user_password_reset_signal = Signal()  # providing_args=["user"]
user_password_changed_signal = Signal()  # providing_args=["user", "password"]
