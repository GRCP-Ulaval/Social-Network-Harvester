from django.contrib.auth.decorators import login_required

from AspiraUser.models import getUserSelection
from Collection.models import Collection, CollectionItem
from Collection.models.Collection import InvalidFieldException
from SocialNetworkHarvester.jsonResponses import jsonNotFound, jResponse, jsonBadRequest, \
    missingParam, jsonForbiddenError, jsonMessages
from SocialNetworkHarvester.loggers.viewsLogger import logError


@login_required
def ajax_base(request, endpoint_name):
    try:
        return {
            'search': search,
            'addItems': addItems,
            'remove_items': removeCollectionItem,
        }[endpoint_name](request)
    except KeyError:
        logError("KeyError occured in collection ajax endpoint")
        return jsonNotFound()
    except InvalidFieldException:
        return jsonBadRequest('Invalid field received.')
    except Exception as e:
        logError('An unknown exception as occured in Collection forms')
        return jResponse({
            'status': 'error',
            'errors': ['Une erreur inconnue est survenue. Veuillez réessayer.']
        })


def search(request):
    query = request.GET.get('query')
    user = request.user

    items = Collection.objects.filter(name__icontains=query)
    items = items | Collection.objects.filter(description__icontains=query)
    items = items | Collection.objects.filter(created_by__first_name__icontains=query)
    items = items | Collection.objects.filter(created_by__last_name__icontains=query)
    return jResponse({
        'data': [item.serialize() for item in items if item not in user.followed_collections.all()]
    })


def addItems(request):
    user = request.user
    get = request.GET

    if not 'pageURL' in get: return missingParam('pageURL')
    if not 'modelName' in get: return missingParam('modelName')
    if not 'tableId' in get: return missingParam('tableId')
    if not 'collection_id' in get: return missingParam('collection_id')

    collection = Collection.objects.filter(pk=get['collection_id']).first()
    if not collection:
        return jsonNotFound()

    if user not in collection.curators.all():
        return jsonForbiddenError()

    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(get['modelName'], get['tableId'])

    for item in queryset:
        CollectionItem.create(collection, item)

    return jsonMessages(
        'Les éléments ont étés ajoutés à la collecte %s.' % collection.name
    )


def removeCollectionItem(request):
    user = request.user
    post = request.POST

    if not 'table_id' in post: return missingParam('table_id')
    if not 'collection_id' in post: return missingParam('collection_id')

    collection = Collection.objects.filter(pk=post['collection_id']).first()
    if not collection:
        return jsonNotFound()

    if user not in collection.curators.all():
        return jsonForbiddenError()

    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(
        "CollectionItem",
        "collection_table_{}".format(post['collection_id'])
    )

    for collection_item in queryset:
        collection_item.delete()

    return jsonMessages(
        "Les éléments sélectionnés ont étés retirés de cette collecte."
    )
