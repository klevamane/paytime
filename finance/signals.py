from __future__ import absolute_import

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from networkdays import networkdays

from finance.models import Investment, RoiSchedule

YEAR = datetime.datetime.now().year
# Holidays
CHRISTMAS = datetime.date(YEAR, 12, 25)
BOXINGDAY = datetime.date(YEAR, 12, 26)
NEWYEAR = datetime.date(YEAR, 1, 1)
NEXTNEWYEAR = datetime.date(YEAR + 1, 1, 1)
LABOUR_DAY = datetime.date(YEAR, 5, 1)
NEXT_LABOUR_DAY = datetime.date(YEAR + 1, 5, 1)
INDEPENDENCE_DAY = datetime.date(YEAR, 10, 1)
EASTER = datetime.date(YEAR, 4, 13)
NEXT_EASTER = datetime.date(YEAR + 1, 4, 13)

HOLIDAYS = {
    CHRISTMAS,
    BOXINGDAY,
    NEWYEAR,
    NEXTNEWYEAR,
    LABOUR_DAY,
    NEXT_LABOUR_DAY,
    INDEPENDENCE_DAY,
    EASTER,
    NEXT_EASTER,
}

days = networkdays.Networkdays(
    datetime.date(2020, 12, 29),  # start date
    datetime.date(2021, 1, 1),  # end date
    HOLIDAYS,  # list of Holidays
)


# Remember to add the signals to the app/apps.py file
# and __init__.py
@receiver(post_save, sender=Investment)
def create_roi(sender, instance, created, **kwargs):
    """
    Create the return on investments days

    This function is taking into cognizant that
    the maximum days should be 90 days

    Args:
        sender: The model triggering the signal
        instance: Model instance
        created: True if the instance is a new instance
        kwargs
    """

    # taking the package days or 90 days
    number_of_wrk_days = instance.package.days or 90
    needed_days = []
    # get the work days for these two dates
    # excluding the holidays
    days_needed = networkdays.Networkdays(
        datetime.date(2020, 12, 29), datetime.date(2021, 12, 29), HOLIDAYS
    ).networkdays()
    # get the days of the month when the user is
    # expected to be paid
    first_end_date = days_needed[:30][-1]
    second_end_date = days_needed[:60][-1]
    needed_days.append(first_end_date)
    needed_days.append(second_end_date)

    if number_of_wrk_days == 90:
        third_end_date = days_needed[:90][-1]
        needed_days.append(third_end_date)
    if created:
        roi_amount = int(
            int(instance.amount) * (instance.package.return_on_investmentent / 100)
        )
        for date in needed_days:
            roi = RoiSchedule(
                investment=instance, maturity_date=date, roi_amount=roi_amount
            )
            roi.save()
