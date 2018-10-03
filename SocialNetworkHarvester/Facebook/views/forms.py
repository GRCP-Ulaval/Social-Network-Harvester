import facebook
from django.contrib.auth.decorators import login_required

from AspiraUser.models import FBAccessToken
from Facebook.models.FBPage import FBPage
from Facebook.models.FBProfile import FBProfile
from SocialNetworkHarvester.jsonResponses import *
from SocialNetworkHarvester.loggers.viewsLogger import logError, viewsLogger, pretty
from tool.views.ajaxTables import readLinesFromCSV

plurial = lambda i: 's' if int(i) > 1 else ''

validFormNames = [
    'FBAddPage',
    'setFacebookToken'
]


@login_required()
def formBase(request, formName):
    if not request.user.is_authenticated: return jsonUnauthorizedError()
    if not formName in validFormNames: return jsonBadRequest('Specified form does not exists')
    try:
        return globals()[formName](request)
    except FacebookAccessTokenException:
        logError('Error while adding FBPages to harvest:')
        return jResponse({
            'status': 'exception',
            'errors': ["Une erreur est survenue avec votre connection Facebook. Visitez votre page de <a class='classic' "
                       "href='/user/settings'>paramètres</a> pour en savoir plus."],
        })
    except:
        logError("ERROR OCCURED IN %s AJAX WITH FORM NAME '%s':" % (__name__, formName))
        return jsonUnknownError()


# @viewsLogger.debug()
def FBAddPage(request):
    if not 'pageUrl' in request.POST and not 'Browse' in request.FILES:
        return jsonBadRequest('No page url specified')
    limit = request.user.userProfile.facebookPagesToHarvestLimit
    currentCount = request.user.userProfile.facebookPagesToHarvest.count()
    if limit <= currentCount:
        return jResponse({
            'status': 'exception',
            'errors': ["Vous avez atteint votre limite de pages à collecter."],
        })

    pageUrls = [url for url in request.POST.getlist('pageUrl') if url != ""]
    invalids = []
    if 'Browse' in request.FILES:
        fileUrls, errors = readLinesFromCSV(request)
        pageUrls += fileUrls
        invalids += errors
    if limit <= currentCount + len(pageUrls):
        pageUrls = pageUrls[:limit - currentCount]
    invalids += addFbPages(request, pageUrls)
    numAddedPages = len(pageUrls) - len(invalids)
    if not numAddedPages:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas un URL valide. Assurez-vous'
                       'qu\'il s\'agit bien d\'une page Facebook publique!' % url for url in invalids],
        })
    return jResponse({
        'status': 'ok',
        'messages': [
            '%s pages publiques %s ont été ajoutées à votre liste (%i erreur%s)' % (
                numAddedPages, plurial(numAddedPages),
                len(invalids), plurial(len(invalids)))]
    })


@viewsLogger.debug(showArgs=True)
def addFbPages(request, pageUrls):
    aspiraProfile = request.user.userProfile
    if not hasattr(aspiraProfile, "fbAccessToken"): raise FacebookAccessTokenException()
    if aspiraProfile.fbAccessToken.is_expired(): raise FacebookAccessTokenException()
    graph = facebook.GraphAPI(aspiraProfile.fbAccessToken._token)
    invalids = []
    response = None
    try:
        response = graph.get_objects(ids=pageUrls)
        pretty(response)
    except Exception as e:
        logError("An error occured")
        return pageUrls
    for url in response.keys():
        if 'name' in response[url] and 'id' in response[url]:
            jUser = graph.get_object(response[url]['id'], fields='name,id')
            fbPage, new = FBPage.objects.get_or_create(_ident=response[url]['id'])
            if new:
                fbProfile, new = FBProfile.objects.get_or_create(_ident=fbPage._ident)
                if new:
                    fbProfile.type = 'P'
                    fbProfile.fbPage = fbPage
                    fbProfile.save()
            fbPage.name = response[url]['name']
            fbPage.save()
            aspiraProfile.facebookPagesToHarvest.add(fbPage)
            aspiraProfile.save()
        else:
            invalids.append(response[url]['id'])
    return invalids


class FacebookAccessTokenException(Exception): pass


@viewsLogger.debug()
def setFacebookToken(request):
    if not 'fbToken' in request.POST: return jsonBadRequest("'fbToken' is required")
    profile = request.user.userProfile
    if not hasattr(profile, 'fbAccessToken'):
        profile.fbAccessToken = FBAccessToken.objects.create()
        profile.save()
    fbAccessToken = profile.fbAccessToken
    fbAccessToken._token = request.POST['fbToken']
    if not request.POST['fbToken']:
        fbAccessToken.expires = None
    else:
        pass
        fbAccessToken.extend()
    fbAccessToken.save()
    profile.facebookApp_parameters_error = False
    profile.save()
    return jsonDone()
