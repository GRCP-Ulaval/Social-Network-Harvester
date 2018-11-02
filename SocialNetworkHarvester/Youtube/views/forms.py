import re

from django.contrib.auth.decorators import login_required
from googleapiclient.discovery import build

from AspiraUser.models import ItemHarvester
from SocialNetworkHarvester.jsonResponses import *
from SocialNetworkHarvester.loggers.viewsLogger import viewsLogger, logError
from SocialNetworkHarvester.utils import validate_harvest_dates, InvalidHarvestDatesException
from Youtube.models import *

plurial = lambda i: 's' if int(i) > 1 else ''

validFormNames = [
    'YTAddChannel',
    'YTAddPlaylist',
]


@login_required()
def formBase(request, formName):
    if not request.user.is_authenticated: return jsonUnauthorizedError()
    if not formName in validFormNames: return jsonBadRequest('Specified form does not exists')
    try:
        return globals()[formName](request)
    except:
        viewsLogger.exception("ERROR OCCURED IN YOUTUBE AJAX WITH FORM NAME '%s'" % formName)
        return jsonUnknownError()


###########  YOUTUBE CHANNELS  ###########
def YTAddChannel(request):
    datasets = [
        (
            request.POST.get('url_0'),
            request.POST.get('since_0'),
            request.POST.get('until_0'),
        ),
        (
            request.POST.get('url_1'),
            request.POST.get('since_1'),
            request.POST.get('until_1'),
        ),
        (
            request.POST.get('url_2'),
            request.POST.get('since_2'),
            request.POST.get('until_2'),
        ),
    ]

    occured_errors = []
    successful_operations = 0
    for dataset in datasets:
        if dataset[0]:  # if first element was specified
            try:
                add_youtube_channel(request.user, *dataset)
                successful_operations += 1
            except AddYoutubeItemHarvesterException as e:
                occured_errors.append(e)

    response = {'status': 'success'}
    if occured_errors:
        response['status'] = 'error',
        response['errors'] = [str(e) for e in occured_errors]
    elif successful_operations:
        plural = successful_operations > 1
        response['messages'] = [
            '{} chaîne{} Youtube {} été ajouté{} à votre liste '
            'de collecte.'.format(
                successful_operations,
                "s" * plural,
                "ont" if plural else "a",
                "s" * plural
            )
        ]
    else:
        response['errors'] = ["Spécifiez au moins un URL de chaine avec sa période de collecte."]
    return jResponse(response)


def add_youtube_channel(user, url, since, until):
    user_profile = user.userProfile
    if user_profile.ytChannelsToHarvest().count() >= user_profile.ytChannelsToHarvestLimit:
        raise AddYoutubeItemHarvesterException(
            'Vous avez atteint la limite de chaînes Youtube pour ce compte! '
            '(limite: {})'.format(user_profile.ytChannelsToHarvestLimit)
        )

    channel_username = get_channel_username_from_url(url)

    youtube_channel = YTChannel.objects.filter(_ident=channel_username).first()
    if not youtube_channel:
        api = get_youtube_api(user_profile)
        youtube_channel = fetch_new_youtube_channel(api, channel_username)

    if ItemHarvester.objects.filter(youtube_channel=youtube_channel, user=user).exists():
        raise AddYoutubeItemHarvesterException(
            'La chaine Youtube "{}" est déjà dans '
            'votre liste de collecte!'.format(youtube_channel)
        )

    try:
        validate_harvest_dates(since, until)
    except InvalidHarvestDatesException as e:
        raise AddYoutubeItemHarvesterException(str(e))

    ItemHarvester.create(user, youtube_channel, since, until)


def get_channel_username_from_url(url):
    match = re.match(r'https?://www.youtube.com/user/(?P<username>[\w\.-]+)/?.*', url)
    if not match:
        match = re.match(r'https?://www.youtube.com/channel/(?P<username>[\w\.-]+)/?.*', url)
    if not match:
        raise AddYoutubeItemHarvesterException(
            '"{}" ne semble pas être une URL valide.'.format(url))
    return match.group('username')


def fetch_new_youtube_channel(api, channel_username):
    try:
        response = api.channels().list(
            id=channel_username,
            part='brandingSettings,contentOwnerDetails,id,'
                 'invideoPromotion,localizations,snippet,statistics,status'
        ).execute()
    except:
        logError("Unknown error while fetching new youtube channel")
        raise AddYoutubeItemHarvesterException(
            'Une erreur est survenue en tentant de trouver '
            'l\'URL spécifiée. Veuillez réessayer.'
        )

    if 'items' not in response or not response['items']:
        raise AddYoutubeItemHarvesterException(
            'L\'url contenant {} ne semble pas correspondre à une chaine '
            'Youtube. Veuillez re-vérifier.'.format(channel_username)
        )
    item = response['items'][0]
    new_channel = YTChannel.objects.create(_ident=item['id'])
    new_channel.update(item)
    return new_channel


###########  YOUTUBE PLAYLISTS  ###########
def YTAddPlaylist(request):
    datasets = [
        (
            request.POST.get('url_0'),
            request.POST.get('since_0'),
            request.POST.get('until_0'),
        ),
        (
            request.POST.get('url_1'),
            request.POST.get('since_1'),
            request.POST.get('until_1'),
        ),
        (
            request.POST.get('url_2'),
            request.POST.get('since_2'),
            request.POST.get('until_2'),
        ),
    ]

    occured_errors = []
    successful_operations = 0
    for dataset in datasets:
        if dataset[0]:  # if first element was specified
            try:
                add_youtube_playlist(request.user, *dataset)
                successful_operations += 1
            except AddYoutubeItemHarvesterException as e:
                occured_errors.append(e)

    response = {'status': 'success'}
    if occured_errors:
        response['status'] = 'error',
        response['errors'] = [str(e) for e in occured_errors]
    elif successful_operations:
        plural = successful_operations > 1
        response['messages'] = [
            '{} playlist{} Youtube {} été ajouté{} à votre liste de '
            'collecte.'.format(
                successful_operations,
                "s" * plural,
                "ont" if plural else "a",
                "s" * plural
            )
        ]
    else:
        response['errors'] = ["Spécifiez au moins un URL de chaine avec sa période de collecte."]
    return jResponse(response)


def add_youtube_playlist(user, url, since, until):
    user_profile = user.userProfile
    if user_profile.ytPlaylistsToHarvest().count() >= user_profile.ytPlaylistsToHarvestLimit:
        raise AddYoutubeItemHarvesterException(
            'Vous avez atteint la limite de playlists Youtube pour ce compte! '
            '(limite: {})'.format(user_profile.ytPlaylistsToHarvestLimit)
        )

    playlist_ident = get_playlist_ident_from_url(url)

    youtube_playlist = YTPlaylist.objects.filter(_ident=playlist_ident).first()
    if not youtube_playlist:
        api = get_youtube_api(user_profile)
        youtube_playlist = fetch_new_youtube_playlist(api, playlist_ident)

    if ItemHarvester.objects.filter(youtube_playlist=youtube_playlist, user=user).exists():
        raise AddYoutubeItemHarvesterException(
            'La playlist Youtube "{}" est déjà dans votre liste de '
            'collecte!'.format(youtube_playlist)
        )

    try:
        validate_harvest_dates(since, until)
    except InvalidHarvestDatesException as e:
        raise AddYoutubeItemHarvesterException(str(e))

    ItemHarvester.create(user, youtube_playlist, since, until)


def get_playlist_ident_from_url(url):
    match = re.match(r'.*list=(?P<ident>[\w\.-]+)&?.*', url)
    if not match:
        raise AddYoutubeItemHarvesterException(
            '"{}" ne semble pas être une URL valide.'.format(url)
        )
    return match.group('ident')


def fetch_new_youtube_playlist(api, playlist_ident):
    try:
        response = api.playlists().list(
            id=playlist_ident,
            part='snippet,id,status'
        ).execute()
    except:
        logError("Unknown error while fetching new youtube playlist")
        raise AddYoutubeItemHarvesterException(
            'Une erreur est survenue en tentant de trouver '
            'l\'URL spécifiée. Veuillez réessayer.'
        )

    if 'items' not in response or not response['items']:
        raise AddYoutubeItemHarvesterException(
            'L\'url contenant {} ne semble pas correspondre à une playlist '
            'Youtube. Veuillez re-vérifier celle-ci.'.format(playlist_ident)
        )
    item = response['items'][0]
    new_playlist = YTPlaylist.objects.create(_ident=item['id'])
    new_playlist.update(item)
    return new_playlist


def get_youtube_api(user_profile):
    try:
        api = build("youtube", "v3", developerKey=user_profile.youtubeApp_dev_key)
        api.i18nLanguages().list(part='snippet').execute()  # testing
        return api
    except:
        user_profile.youtubeApp_parameters_error = True
        user_profile.save()
        logError('Error in Youtube forms: get_youtube_api')
        raise AddYoutubeItemHarvesterException(
            "Un problème est survenu avec votre application Youtube! Veuillez "
            "visiter votre page de <a href='/user/settings' "
            "class='TableToolLink'>paramètres</a> et assurez-vous que les "
            "informations inscrites dans la section \"Youtube\" sont correctes."
        )


class AddYoutubeItemHarvesterException(Exception):
    pass
