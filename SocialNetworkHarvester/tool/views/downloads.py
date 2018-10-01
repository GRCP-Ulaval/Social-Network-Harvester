import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import *

from AspiraUser.models import getUserSelection
from SocialNetworkHarvester.jsonResponses import *
from SocialNetworkHarvester.settings import DEBUG, STATIC_ROOT, STATICFILES_DIRS


@login_required
def downloadMedia(request):
    if not 'file' in request.GET: return jsonBadRequest('You must specify a filename')
    fileName = request.GET['file']
    if '..' in fileName: raise Http404()
    if DEBUG:
        filePath = os.path.join(STATICFILES_DIRS[0], 'medias/%s' % fileName)
    else:
        filePath = os.path.join(STATIC_ROOT, 'medias/%s' % fileName)
    if not os.path.exists(filePath): raise Http404()
    with open(filePath, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=%s' % fileName
        return response
    pdf.closed


@login_required
def downloadProgress(request):
    tableRowsSelections = getUserSelection(request)

    options = tableRowsSelections.getQueryOptions(request.GET['tableId'])
    if not 'downloadProgress' in options:
        tableRowsSelections.setQueryOption(request.GET['tableId'], 'downloadProgress', 0)
        options = tableRowsSelections.getQueryOptions(request.GET['tableId'])
    return HttpResponse(json.dumps(options), content_type='application/json')
