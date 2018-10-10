from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from AspiraUser.models import resetUserSelection
from Collection.models import Collection


@login_required()
def collections_dashboard(request):
    context = {
        'user': request.user,
        "navigator": [
            ("Collectes", "/collection"),
        ],
    }
    resetUserSelection(request)
    return render(request, 'Collection/containers/Collection_Dashboard.html', context)


def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    context = {
        "navigator": [
            ("Collectes", "/collection"),
            (collection, "/collection/%s" % collection.pk),
        ],
        "collection": collection,
    }
    resetUserSelection(request)
    return render(request, "Collection/containers/Collection_Details.html", context)
