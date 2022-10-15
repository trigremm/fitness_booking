import logging
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from users.signals import user_password_changed_signal, user_password_reset_signal

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        if self.filter(email=email).exists():
            raise ValueError("Duplicate email")
        if not password:
            raise ValueError("User must have a password")
        user = User.objects.model(email=email, **extra_fields)
        user.set_password(password)  # change password to hash
        user.token = user.generate_token()
        user.token = str(uuid.uuid4()).replace("-", "")
        user.is_active = False
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        # а в документации по другому
        # https://docs.djangoproject.com/en/4.1/topics/auth/customizing/
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email=email, password=password, **extra_fields)

    def user_password_reset(self, email):
        # FUTURE DEVELOPMENT django-rest-passwordreset
        email = self.normalize_email(email)
        queryset = self.filter(email=email)
        if queryset.exists() is False:
            raise ValueError("User not found")
        if queryset.count() > 1:
            logger.warning("MultipleObjectsReturned for email: %s", email)
        for user in queryset:
            # user.is_active = False # it was decided not to change the is_active state
            user.token = self.generate_token(user)
            user.save()
            logger.info("user_password_reset for user: %s", user)
            user_password_reset_signal.send(sender=User, user=user)
        return True

    def user_password_change(self, user, password):
        user.token = None
        # user.is_active = True # it was decided not to change the is_active state
        user.set_password(password)
        user.save()
        logger.info("user_password_changed for user: %s", user)
        user_password_changed_signal.send(sender=User, user=user, password=password)
        return True

    def delete_user(self, user):
        prefix = f"""deleted_at_{timezone.now().strftime('%Y%m%d_%H%M%S')}"""
        user.email = f"{prefix}_{user.email}"
        # user.deleted_at = timezone.now() #  'User' object has no attribute 'deleted_at'
        user.is_active = False
        user.save()
        return True


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    token = models.CharField(max_length=50, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        # not sure about either to use [if name is not None else ""] or [or] condition
        return f"""{self.last_name or ""} {self.first_name or ""}"""

    def generate_token(self):
        return default_token_generator.make_token(self)
