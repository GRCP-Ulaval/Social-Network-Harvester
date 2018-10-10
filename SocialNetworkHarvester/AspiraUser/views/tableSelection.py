from django.contrib.auth.decorators import login_required

from AspiraUser.models import getUserSelection
from SocialNetworkHarvester.jsonResponses import *
from SocialNetworkHarvester.loggers.viewsLogger import logError


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
    if addRemove not in ['add', 'remove']: return jsonBadRequest("bad command: %s" % addRemove)
    for attr in ['id', 'list']:
        if not attr in request.POST: return jsonBadRequest("missing parameter: %s" % attr)
    id = request.POST['id']
    listName = request.POST['list']
    listLimit = listName + 'Limit'

    user = request.user
    if not hasattr(user.userProfile, listName): return jsonBadRequest("no such list: %s" % listName)
    list = getattr(user.userProfile, listName)
    limit = getattr(user.userProfile, listLimit)
    model = list.model

    if not model.objects.filter(pk=id).exists(): return jsonBadRequest(
        'item #%s of type "%s" does not exists' % (id, model))
    item = model.objects.filter(pk=id).first()

    if addRemove == 'add':
        if item in list.all(): return jsonBadRequest("%s is already in current list" % item)
        if limit != 0 and list.count() >= limit:
            return jsonBadRequest("Vous avez atteint la limite pour cette liste de collecte. (%s éléments)" % limit)
        list.add(item)
        return jResponse(
            {'message': {"code": 200, "message": "<b>%s</b> as été ajouté de votre liste de collecte." % item}})
    else:
        if not item in list.all(): return jsonBadRequest("%s is not in current list" % item)
        list.remove(item)
        return jResponse(
            {'message': {"code": 200, "message": "<b>%s</b> as été retiré de votre liste de collecte." % item}})
