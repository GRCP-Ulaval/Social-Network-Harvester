import time
from datetime import datetime, timedelta
from random import random

from django.core.exceptions import MultipleObjectsReturned
from django.db import models, IntegrityError
from django.utils.timezone import now, utc


def djangoNow():
    return now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def today():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def xDaysAgo(n=0):
    return today() - timedelta(days=n)


def get_from_any_or_create(table, **kwargs):
    '''
    Retrieves an object from any of the attributes. If any attribute in <kwargs> matches an entry in <table>, then the
    entry is returned, otherwise an object is created using all the attributes.
    '''
    kwargs = {kwarg: kwargs[kwarg] for kwarg in kwargs.keys() if kwargs[kwarg]}  # eliminate "None" values
    item = None
    for param in kwargs.keys():
        if not item:
            try:
                item = table.objects.get(**{param: kwargs[param]})
            except models.ObjectDoesNotExist:
                continue
            except MultipleObjectsReturned:
                item = table.objects.filter(**{param: kwargs[param]}).first()
            except:
                raise
        else:
            setattr(item, param, kwargs[param])
    if item:
        item.save()
        return item, False
    else:
        try:
            item = table.objects.create(**kwargs)
        except IntegrityError:  # sometimes the table entry is created while this run...
            return get_from_any_or_create(table, **kwargs)
        return item, True
