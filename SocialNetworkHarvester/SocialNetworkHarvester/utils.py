from datetime import datetime, timedelta

from django.core.exceptions import MultipleObjectsReturned
from django.db import models, IntegrityError
from django.utils.timezone import now, utc

from SocialNetworkHarvester.settings import HARVEST_SINCE_OLDEST_DATE, HARVEST_MAX_PERIOD


def djangoNow():
    return now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def today():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def x_days_ago(n=0):
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


def validate_harvest_dates(harvest_since, harvest_until):
    if not harvest_since or not harvest_until:
        raise InvalidHarvestDatesException('Veuillez spécifier les dates de début et de fin.')
    try:
        since = datetime.strptime(harvest_since, '%Y-%m-%d').replace(tzinfo=utc)
        until = datetime.strptime(harvest_until, '%Y-%m-%d').replace(tzinfo=utc)
    except ValueError:
        raise InvalidHarvestDatesException(f"L'une des dates spécifiée {harvest_since}, "
                                           f"{harvest_until} est invalide.")
    if since >= until:
        raise InvalidHarvestDatesException('La date de fin doit être après la date de début!')
    if since + HARVEST_MAX_PERIOD < until:
        raise InvalidHarvestDatesException(
            f"La durée maximale d'une collecte est de {HARVEST_MAX_PERIOD.days} jours."
        )
    if since + HARVEST_SINCE_OLDEST_DATE < today():
        raise InvalidHarvestDatesException(
            f"La date de début d'une collecte ne peut pas remonter à avant les 6 derniers mois. "
            f"Limite actuelle: {(today()-HARVEST_SINCE_OLDEST_DATE).strftime('%Y-%m-%d')}."
        )


class InvalidHarvestDatesException(Exception):
    pass
