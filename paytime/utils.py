from __future__ import absolute_import

import logging
from smtplib import SMTPSenderRefused

from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.http import HttpResponse, HttpResponseRedirect

log = logging.getLogger("api")


def send_email(subject, body, from_email, to):
    if subject and body and from_email:
        try:
            email = EmailMessage(subject, body, from_email, [to])
            email.send(fail_silently=False)
        except BadHeaderError:
            return HttpResponse("Invalid header found")
        except SMTPSenderRefused as e:
            log.info(e)
            log.info("If using google mail, allow access for less secure apps")
    else:
        # Todo we can use a form class to get
        # proper validation
        return HttpResponse("Ensure all fields are entered and are valid")


SUCCESS_MESSAGES = {
    "account_created": "Your account has been created, check your inbox for a verification email"
}
