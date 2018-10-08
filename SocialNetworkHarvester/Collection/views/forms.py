import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404

from Collection.models import Collection
from SocialNetworkHarvester.loggers.viewsLogger import pretty, logError
from SocialNetworkHarvester.settings import DEBUG
from SocialNetworkHarvester.views.messages import add_error_message, add_info_message


@login_required
def form_base(request, form_name):
    try:
        return {
            'create': create_collection,
            'unsubscribe': unsubscribe_from_collection,
            'subscribe': subscribe_to_collections
        }[form_name](request)
    except KeyError:
        return HttpResponseBadRequest('Invalid form name')
    except Exception as e:
        logError('An unknown exception as occured in Collection forms')
        add_error_message(request, 'Une erreur inconnue est survenue{}. Veuillez réessayer.'
                          .format(' ({})'.format(e) if DEBUG else ''))
        return redirect(request.META.get('HTTP_REFERER'))


def create_collection(request):
    def error(message):
        add_error_message(request, message)
        return redirect('/collection')

    post = request.POST
    pretty(post)
    if not post['name']: return error('Le paramètre "nom" est obligatoire')
    name = post['name']

    if Collection.objects.filter(name=name).exists():
        return error('Une collecte avec ce nom existe déja. Essayez à nouveau.')

    if not post['harvest_start']: return error('Le paramètre "Début de collecte" est obligatoire')
    harvest_start = post['harvest_start']

    if not post['harvest_end']: return error('Le paramètre "Fin de collecte" est obligatoire')
    harvest_end = post['harvest_end']

    start = datetime.strptime(harvest_start, '%Y-%m-%d')
    end = datetime.strptime(harvest_end, '%Y-%m-%d')
    if start >= end:
        return error('La fin de la collecte doit être après son début!')

    active = 'active' in post

    description = None
    if 'description' in post:
        description = post['description']

    collection = Collection.objects.create(
        name=name,
        description=description,
        harvest_end=harvest_end,
        harvest_start=harvest_start,
        harvest_is_active=active,
        created_by=request.user
    )

    collection.curators.add(request.user)
    collection.followers.add(request.user)
    collection.save()

    add_info_message(request, "La collecte \"{}\" as bien été créée!".format(name))
    return redirect('/collection')


def unsubscribe_from_collection(request):
    collection_id = request.POST.get('collection')
    collection = get_object_or_404(Collection, pk=collection_id)
    user = request.user
    collection.followers.remove(user)
    add_info_message(request, "Vous avez bien été désabonné de la collecte\"{}\".".format(collection.name))
    return redirect(request.META.get('HTTP_REFERER'))


def subscribe_to_collections(request):
    ids_str = list(filter(lambda s: re.match('collection_id_\d+', s), request.POST.keys()))
    ids = list(map(lambda s: int(re.sub('collection_id_', '', s)), ids_str))
    user = request.user
    for id in ids:
        collection = get_object_or_404(Collection, id=id)
        collection.followers.add(user)
    if ids:
        add_info_message(request, "Votre abonnement à {} collecte{} s'est effectué avec succès!".format(
            len(ids), 's' if len(ids) > 1 else ''
        ))
    return redirect(request.META.get('HTTP_REFERER'))
