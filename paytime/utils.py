from __future__ import absolute_import

import logging
from smtplib import SMTPSenderRefused

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from six import text_type

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
    "account_created": "Your account has been created, check your inbox for a verification email",
    "verified": "Your email has been verified, proceed to login",
}


class TokenGenerator(PasswordResetTokenGenerator):
    # override this method in PasswordResetTokenGenerator
    def _make_hash_value(self, user, timestamp):
        # using text_type to ensure that the returned value
        # is compatible with functions/services that will make use of this
        # if used after the first use, it will indicated that it has been used
        # check the docs for the actual function in the PasswordResetTokenGenerator
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


token_generator = TokenGenerator()
