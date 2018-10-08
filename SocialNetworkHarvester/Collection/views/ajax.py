from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from Collection.models import Collection
from Collection.models.Collection import InvalidFieldException
from SocialNetworkHarvester.jsonResponses import jsonUnknownError, jsonNotFound, jResponse, jsonBadRequest
from SocialNetworkHarvester.loggers.viewsLogger import logError


@login_required
def ajax_base(request, endpoint_name):
    try:
        return {
            'search': search,
        }[endpoint_name](request)
    except KeyError:
        return jsonNotFound()
    except InvalidFieldException:
        return jsonBadRequest('Invalid field received.')
    except Exception as e:
        logError('An unknown exception as occured in Collection forms')
        return jsonUnknownError()


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
