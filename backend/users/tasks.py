from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


@shared_task
def send_email_background(email, template, context):
    _template = get_template(template)
    html_content = _template.render(context)

    msg = EmailMultiAlternatives("Registration", html_content, FROM_EMAIL, [email])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return "Send"


@shared_task
def shared_task_send_email(  # pylint: disable=invalid-name
    subject,
    body,
    to,
    attach_tuples=None,
    template=None,
):
    _template = get_template(template) if template else None
    html_content = _template.render({"message": body}) if _template else body
    msg = EmailMultiAlternatives(subject, html_content, FROM_EMAIL, [to])
    msg.content_subtype = "html"  # Main content is now text/html
    if attach_tuples:
        for name, file in attach_tuples:
            msg.attach(name, open(file, "rb").read())
    msg.send()
    return "sent"


@shared_task
def shared_task_send_email_user_created(context):
    email = context.get("email")
    # name = context.get("name")
    # login = context.get("login")
    # password = context.get("password")

    subject = "Congratulations! Your account has been created"
    # body = mailing.message
    # body = body.replace("<name>", name)
    # body = body.replace("<login>", login)
    # body = body.replace("<password>", password)
    body = context
    to = email  # pylint: disable=invalid-name
    attach_tuples = []
    template = None

    shared_task_send_email.delay(subject, body, to, attach_tuples, template)
