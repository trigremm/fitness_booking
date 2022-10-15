import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .signals import (
    user_password_changed_signal,
    user_password_reset_signal,
)
from shared.utils import send_simple_email
from django.conf import settings

FRONTEND_URL = settings.FRONTEND_URL
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save_receiver(sender, user, created, *args, **kwargs):  # pylint: disable=unused-argument
    """
    after saved in the database
    """
    if created:
        activation_url = f"{FRONTEND_URL}/auth/activate/?token={user.token}"
        context = {
            "subject": "account successfully created",
            "message": f"account successfully created\n\nactivate your account by clicking on the link below\n\n{activation_url}",
            "email_to": user.email,
        }
        try:
            send_simple_email(context)
            logger.info("USER_CREATED email is sent")
        except Exception as error:  # pylint: disable=broad-except
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"USER_CREATED email is not sent, {context=} {error=}"
            )


# @receiver(user_password_reset_signal, sender=User)
# def user_password_reset_receiver(sender, user, *args, **kwargs):  # pylint: disable=unused-argument
#     """
#     after forgot email button pressed
#     """

#     logger.info("PASSWORD_RECOVERY email enqueueing")
#     url = settings.FRONTEND_URL

#     password_link = url.rstrip("/") + "/forgot-password?token=" + user.token
#     context = {
#         "email": user.email,
#         "name": user.full_name,
#         "password_link": password_link,
#     }
#     shared_task_send_email_password_recovery.delay(context)
#     logger.info("PASSWORD_RECOVERY email is sent")


# @receiver(user_password_changed_signal, sender=User)
# def user_password_changed_receiver(sender, user, *args, **kwargs):  # pylint: disable=unused-argument
#     pass
