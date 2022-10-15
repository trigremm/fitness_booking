from django.core.mail import send_mail
from django.conf import settings

EMAIL_FROM = settings.EMAIL_HOST_USER


def send_simple_email(context):
    subject = context.get("subject")
    message = context.get("message")
    email_to = context.get("email_to")
    return send_mail(
        subject=subject,
        message=message,
        from_email=EMAIL_FROM,
        recipient_list=[email_to],
    )
