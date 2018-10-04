from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from AspiraUser.models import resetUserSelection


@login_required()
def collections_dashboard(request):

    context = {
        'user': request.user,
        "navigator": [
            ("Collectes", "/collection"),
        ],
    }
    resetUserSelection(request)

    return render(request, 'Collection/Collection_Dashboard.html', context)
