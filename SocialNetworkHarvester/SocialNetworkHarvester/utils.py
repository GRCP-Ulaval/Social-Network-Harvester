from datetime import datetime, timedelta

from django.utils.timezone import now, utc


def djangoNow():
    return now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def today():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def xDaysAgo(n=0):
    return today() - timedelta(days=n)
