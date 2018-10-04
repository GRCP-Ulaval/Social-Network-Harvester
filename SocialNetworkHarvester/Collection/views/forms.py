from django.shortcuts import redirect

from SocialNetworkHarvester.loggers.viewsLogger import pretty


def create_collection(request):
    pretty(request.POST)
    return redirect(request.META.get('HTTP_REFERER'))
