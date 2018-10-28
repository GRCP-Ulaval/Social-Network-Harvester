from django.contrib.auth.decorators import login_required

from AspiraUser.models import getUserSelection, getModel, ItemHarvester, resetUserSelection
from SocialNetworkHarvester.jsonResponses import jsonBadRequest, missingParam, jResponse, jsonMessages
from SocialNetworkHarvester.loggers.viewsLogger import logError
from SocialNetworkHarvester.utils import validate_harvest_dates, InvalidHarvestDatesException


@login_required()
def removeSelectedItems(request):
    """ Removes the selecteds ItemHarvesters from the user's harvesting list
    """
    user = request.user
    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(None, request.GET['tableId'])
    count = queryset.count()
    try:
        for item in queryset:
            user.userProfile.remove_item_from_harvest_list(item)
    except Exception:
        logError('An error occured while removing selection from harvesting list')
        return jResponse({
            'error': {
                'code': 500, 'message': 'Une erreur est survenue. Veuillez réessayer.'
            }
        })
    resetUserSelection(request)
    return jsonMessages([f"{count} élément{'s' if count>1 else ''} "
                         f"{'ont' if count>1 else 'a'} été retiré{'s' if count>1 else ''} "
                         f"de votre liste de collecte."]
                        )


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
        return jResponse({
            'messages': [f"<b>{item}</b> as été ajouté à votre liste de collecte."]
        })
    else:
        if not user.userProfile.item_is_in_list(item):
            return jsonBadRequest(f"{item} is not in current list")

        user.userProfile.remove_item_from_harvest_list(item)

        return jResponse({
            "messages": [f"<b>{item}</b> as été retiré de votre liste de collecte."]
        })
