import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import utc

from AspiraUser.models import getUserSelection, getModel, ItemHarvester
from SocialNetworkHarvester.jsonResponses import jsonBadRequest, missingParam, jResponse
from SocialNetworkHarvester.loggers.viewsLogger import logError
from SocialNetworkHarvester.settings import HARVEST_MAX_PERIOD, HARVEST_SINCE_OLDEST_DATE
from SocialNetworkHarvester.utils import today


@login_required()
def removeSelectedItems(request):
    errors = []
    userProfile = request.user.userProfile
    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(None, request.GET['tableId'])
    successNum = 0
    listToRemovefrom = getattr(userProfile, request.GET['listToRemoveFrom'])
    for item in queryset:
        try:
            listToRemovefrom.remove(item)
            successNum += 1
        except:
            logError('Une erreur est survenue lors du retrait de %s' % item)
            errors.append('Une erreur est survenue lors du retrait de %s' % item)
    if errors == []:
        response = {'status': 'ok', 'messages': [
            'Retiré %i élément%s de votre liste de collecte' % (successNum, 's' if successNum > 1 else '')]}
    else:
        response = {'status': 'exception', 'errors': errors}
    selection.delete()
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required()
def addRemoveItemById(request, addRemove):
    if addRemove not in ['add', 'remove']: return jsonBadRequest("Bad command: %s" % addRemove)
    for attr in ['id', 'model', 'harvest_since', 'harvest_until']:
        if attr not in request.POST:
            return missingParam(attr)
    user = request.user
    item_id = request.POST['id']
    model = getModel(request.POST['model'])

    harvest_since = request.POST['harvest_since']
    harvest_until = request.POST['harvest_until']

    limit = user.userProfile.get_harvest_limit(model)
    if not model.objects.filter(pk=item_id).exists():
        return jsonBadRequest('Item #%s of type "%s" does not exists' % (item_id, model))

    item = model.objects.filter(pk=item_id).first()
    harvesteds = user.userProfile.get_harvest_queryset(item.__class__)

    if addRemove == 'add':

        try:
            validate_harvest_dates(harvest_since, harvest_until)
        except InvalidHarvestDatesException as e:
            return jsonBadRequest(str(e))

        if user.userProfile.item_is_in_list(item):
            return jsonBadRequest(f"{item} Est déjà dans votre liste de collecte!")

        if limit != 0 and harvesteds.count() >= limit:
            return jsonBadRequest(
                f"Vous avez atteint la limite pour cette liste de collecte ({limit} éléments)."
            )

        ItemHarvester.create(user, item, harvest_since, harvest_until)
        return jResponse(
            {'message': {"code": 200, "message": "<b>%s</b> as été ajouté de votre liste de collecte." % item}})
    else:
        if not user.userProfile.item_is_in_list(item):
            return jsonBadRequest(f"{item} is not in current list")

        user.userProfile.get_item_harvester(item).delete()

        return jResponse(
            {'message': {
                "code": 200, "message": f"<b>{item}</b> as été retiré de votre liste de collecte."}
            }
        )


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
