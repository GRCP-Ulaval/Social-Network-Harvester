import re
from datetime import datetime

import tweepy
from django.contrib.auth.decorators import login_required

from AspiraUser.models import ItemHarvester
from SocialNetworkHarvester.jsonResponses import *
from SocialNetworkHarvester.loggers.viewsLogger import logError, log
from SocialNetworkHarvester.utils import validate_harvest_dates, InvalidHarvestDatesException
from Twitter.models import *


@login_required()
def addUser(request):
    for key in ['screen_name_0', 'since_0', 'until_0', 'screen_name_1', 'since_1',
                'until_1', 'screen_name_2', 'since_2', 'until_2']:
        if key not in request.POST:
            return missingParam(key)

    datasets = [
        (
            request.POST.get('screen_name_0'),
            request.POST.get('since_0'),
            request.POST.get('until_0'),
        ),
        (
            request.POST.get('screen_name_1'),
            request.POST.get('since_1'),
            request.POST.get('until_1'),
        ),
        (
            request.POST.get('screen_name_2'),
            request.POST.get('since_2'),
            request.POST.get('until_2'),
        ),
    ]

    occured_errors = []
    successful_operations = 0
    for dataset in datasets:
        if dataset[0]:  # if first_element was specified
            try:
                add_twitter_user(request.user, *dataset)
                successful_operations += 1
            except AddTwitterHarvestItemException as e:
                occured_errors.append(e)
            except Exception:
                logError("An unknown error occured while adding a new Twitter user.")
                return jsonErrors(['Une erreur inconnue est survenue. Veuillez réessayer'])

    response = {'status': 'success'}
    if occured_errors:
        response['status'] = 'error',
        response['errors'] = [str(e) for e in occured_errors]
    if successful_operations:
        plural = successful_operations > 1
        response['messages'] = [
            f'{successful_operations} utilisateur{"s"*plural} {"ont" if plural else "a"} '
            f'été ajouté{"s"*plural} à votre liste de collecte.'
        ]
    return jResponse(response)


def add_twitter_user(user, screen_name, since, until):
    user_profile = user.userProfile

    if user_profile.twitterUsersToHarvest().count() >= user_profile.twitterUsersToHarvestLimit:
        raise AddTwitterHarvestItemException(
            f'Vous avez atteint la limite d\'utilisateurs Twitter pour ce compte! '
            f'(limite: {user_profile.twitterUsersToHarvestLimit})'
        )

    twitter_user = TWUser.objects.filter(screen_name=screen_name).first()
    if not twitter_user:
        api = getTwitterApi(user_profile)
        twitter_user = fetch_new_twitter_user(api, screen_name)

    if ItemHarvester.objects.filter(twitter_user=twitter_user, user=user).exists():
        raise AddTwitterHarvestItemException(f'L\'utilisateur "{screen_name}" est déjà dans votre liste de collecte!')

    try:
        validate_harvest_dates(since, until)
    except InvalidHarvestDatesException as e:
        raise AddTwitterHarvestItemException(str(e))

    ItemHarvester.create(user, twitter_user, since, until)


def fetch_new_twitter_user(api, screen_name):
    try:
        response = api.lookup_users(screen_names=[screen_name])[0]._json
    except tweepy.error.TweepError as e:
        if e.api_code == 17:
            raise AddTwitterHarvestItemException(
                f'Aucun utilisateur Twitter ne correspond au screen_name "{screen_name}"'
            )
        else:
            raise
    new_user = TWUser.objects.create(_ident=response['id'])
    new_user.UpdateFromResponse(response)
    return new_user


def getTwitterApi(userProfile):
    if not all([
        userProfile.twitterApp_access_token_key,
        userProfile.twitterApp_access_token_secret,
        userProfile.twitterApp_consumerKey,
        userProfile.twitterApp_consumer_secret
    ]):
        raise AddTwitterHarvestItemException(
            "Vous devez d'abord configurer votre application Twitter! Veuillez visiter votre page de "
            "<a href='/user/settings' class='TableToolLink'>paramètres</a> et suivre la procédure "
            "décrite dans la section \"Twitter\"."
        )
    try:
        auth = tweepy.OAuthHandler(
            userProfile.twitterApp_consumerKey,
            userProfile.twitterApp_consumer_secret
        )
        auth.set_access_token(userProfile.twitterApp_access_token_key, userProfile.twitterApp_access_token_secret)
        api = tweepy.API(auth)
        api.me()
        return api
    except tweepy.error.TweepError as e:
        if e.api_code == 32:
            userProfile.twitterApp_parameters_error = True
            userProfile.save()
            logError('Error in Twitter.forms.py: addUser')
            raise AddTwitterHarvestItemException(
                "Un problème est survenu avec votre application Twitter! Veuillez visiter votre page de "
                "<a href='/user/settings' class='TableToolLink'>paramètres</a> et assurez-vous que les "
                "informations inscrites dans la section \"Twitter\" sont correctes."
            )
        else:
            raise


@login_required()
def addHashtag(request):
    datasets = [
        (
            request.POST.get('term_0'),
            request.POST.get('since_0'),
            request.POST.get('until_0'),
        ),
        (
            request.POST.get('term_1'),
            request.POST.get('since_1'),
            request.POST.get('until_1'),
        ),
        (
            request.POST.get('term_2'),
            request.POST.get('since_2'),
            request.POST.get('until_2'),
        ),
    ]

    occured_errors = []
    successful_operations = 0
    for dataset in datasets:
        if dataset[0]:  # if first element was specified
            try:
                add_twitter_hashtag(request.user, *dataset)
                successful_operations += 1
            except AddTwitterHarvestItemException as e:
                occured_errors.append(e)

    response = {'status': 'success'}
    if occured_errors:
        response['status'] = 'error',
        response['errors'] = [str(e) for e in occured_errors]
    elif successful_operations:
        plural = successful_operations > 1
        response['messages'] = [
            f'{successful_operations} hashtags{"s"*plural} Twitter {"ont" if plural else "a"} '
            f'été ajouté{"s"*plural} à votre liste de collecte.'
        ]
    else:
        response['errors'] = ["Spécifiez au moins un Hashtag avec sa période de collecte."]
    return jResponse(response)


def add_twitter_hashtag(user, term, since, until):
    user_profile = user.userProfile
    if user_profile.twitterHashtagsToHarvest().count() >= user_profile.twitterHashtagsToHarvestLimit:
        raise AddTwitterHarvestItemException(
            f'Vous avez atteint la limite de hashtag Twitter pour ce compte! '
            f'(limite: {user_profile.twitterHashtagsToHarvestLimit})'
        )

    if not re.match('^#?[a-zA-z0-9_]+$', term):
        raise AddTwitterHarvestItemException(
            'Un hashtag Twitter ne peut que contenir des caractères simples (a-z, A-Z, 0-9).'
        )

    twitter_hashtag, new = Hashtag.objects.get_or_create(term=term)

    if ItemHarvester.objects.filter(twitter_hashtag=twitter_hashtag, user=user).exists():
        raise AddTwitterHarvestItemException(
            f'Le hashtag "{twitter_hashtag}" est déjà dans '
            f'votre liste de collecte!'
        )

    try:
        validate_harvest_dates(since, until)
    except InvalidHarvestDatesException as e:
        raise AddTwitterHarvestItemException(str(e))

    ItemHarvester.create(user, twitter_hashtag, since, until)


class AddTwitterHarvestItemException(Exception):
    pass
