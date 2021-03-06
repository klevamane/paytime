from __future__ import absolute_import

import functools
import logging
import time
from smtplib import SMTPSenderRefused

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, EmailMessage
from django.db import connection, reset_queries
from django.http import HttpResponse
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
    "msg_sent_to_admin": "Your message has been sent to the admin",
    "kindly_verify": "Hi {} kindly use this link to verify your account\n {}",
    "verified": "Your email has been verified, proceed to login",
    "operation_successful": "The {} was successful",
    "no_otp_transfer": "Transfer is not currently awaiting OTP",
    "upload_successful": "{} uploaded successfully",
    "blank_successful": "{} successful",
}

FAILURE_MESSAGES = {
    "account_not_active": "Your account is not active, please contact the adminstrator",
    "alpa_num_only": "Enter only alphanumeric characters",
    "amount_mis_match": "We experienced an amount mismatch, we have instead updated your wallet",
    "amount_specific_range": "The amount must be in the range of {} to {}",
    "cannot_add_multiple_bank": "You cannot add multiple bank accounts, try updating instead",
    "cannot_update_bank": "You cannot update your bank account. Kindly contact us to proceed",
    "enter_valid_amount": "Enter a valid amount",
    "enter_valid_number": "Enter a valid {}",
    "funds_too_low": "Wallet balance is too low",
    "file_size_limit": "The {} size should not be greater than {}",
    "insufficient_funds": "Insufficient Funds",
    "incomplete_unverifiable_tnx": "Transaction not completed, unable to verify transaction",
    "invalid_method": "Method should be {}",
    "invalid": "invalid {}",
    "min_gt_max": "The maximum amount must be greater than the minimum amount",
    "not_found": "The {} was not found",
    "select_pkg_for_amt": "Select a valid package for this amount",
    "specify_account_digits": "{} digit account number is required",
    "something_went_wrong": "Something went wrong",
    "unsupported_file_type": "The file type is not supported, kindly upload a supported file",
    "user_has_active_investment": "You already have an active investment, so you cannot make any other payment",
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


def query_debugger(func):
    """Get the number of queries used in a function

    This decorator gets the number of queries used in a function
    and the time taken

    Args:
        func: The function to be decorated
    """

    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        # reset saved queries when a Django request is started
        reset_queries()

        begin_queries = len(connection.queries)

        start_time = time.perf_counter()
        response = func(*args, **kwargs)
        end_time = time.perf_counter()

        stop_queries = len(connection.queries)

        print("Function name ->> {}".format(func.__name__))
        print("Number of Queries ->> {}".format(stop_queries - begin_queries))
        print("Completed in ->> {}s".format(end_time - start_time))
        return response

    return inner_func
