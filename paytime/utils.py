from __future__ import absolute_import

import logging
from smtplib import SMTPSenderRefused

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
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
    "bank_account_added": "Your bank account has been added",
    "bank_account_updated": "Your bank account has been updated",
    "already_activated": "Your email is already verified and activated",
    "kindly_verify": "Hi {} kindly use this link to verify your account\n {}",
    "verified": "Your email has been verified, proceed to login",
}

FAILURE_MESSAGES = {
    "account_not_active": "Your account is not active, please contact the adminstrator",
    "cannot_add_multiple_bank": "You cannot add multiple bank accounts, try updating instead",
    "cannot_update_bank": "You cannot update your bank account. Kindly contact us to proceed",
}


class TokenGenerator(PasswordResetTokenGenerator):
    logging.info("Deprecated: We are now making use of allauth token generator")

    # override this method in PasswordResetTokenGenerator
    def _make_hash_value(self, user, timestamp):
        # using text_type to ensure that the returned value
        # is compatible with functions/services that will make use of this
        # if used after the first use, it will indicated that it has been used
        # check the docs for the actual function in the PasswordResetTokenGenerator
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


token_generator = TokenGenerator()

NG_MOBILE_PREFIXES = {
    "mtn": [
        "0803",
        "0703",
        "0903",
        "0806",
        "0706",
        "0813",
        "0814",
        "0816",
        "0810",
        "0906",
        "07025",
        "07026",
        "0704",
    ],
    "glo": ["0805", "0705", "0905", "0807", "0815", "0905", "0811"],
    "airtel": ["0802", "0902", "0701", "0808", "0708", "0812", "0901", "0907"],
    "9mobile": ["0809", "0909", "0817", "0818", "0908"],
    "ntel": ["0804"],
    "smile": ["0702"],
    "multilinks": ["0709", "07027"],
    "visafone": ["07025", "07026", "0704"],
    "starcomms": ["07028", "07029", "0819"],
    "zoom": ["0707"],
}


def validate_ng_mobile_number(mobile_number):
    try:
        int(mobile_number)
    except ValueError:
        raise ValidationError(_("Enter a valid Nigerian mobile number"), code=400)
    if len(mobile_number) != 11:
        raise ValidationError("Enter 11 digit mobile number", code=400)
    # check if it starts with any prefix [0807,0906 etc..]
    if mobile_number[:1] != "0" and (
        (
            mobile_number[:5] in NG_MOBILE_PREFIXES
            or mobile_number[:4] in NG_MOBILE_PREFIXES
        )
    ):
        raise ValidationError(_("Enter a valid Nigerian mobile number"))
