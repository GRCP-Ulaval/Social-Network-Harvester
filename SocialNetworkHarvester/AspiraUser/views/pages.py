from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, HttpResponseRedirect, Http404
from django.utils.timezone import utc

from AspiraUser.models import UserProfile, resetUserSelection
from Facebook.models import FBPost, FBPage
from SocialNetworkHarvester.jsonResponses import *
from Youtube.models import *
from tool.views.ajaxTables import digestQuery, cleanQuery


def lastUrlOrHome(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect('/')


@login_required()
def userDashboard(request):
    resetUserSelection(request)
    aspiraUser = request.user.userProfile
    context = {
        'user': request.user,
        "navigator": [
            ("Tableau de bord", "/"),
        ],
        "twStats": getTwitterStats(aspiraUser),
        "ytStats": getYoutubeStats(aspiraUser),
        "fbStats": getFacebookStats(aspiraUser),
    }
    return render(request, 'AspiraUser/dashboard.html', context)


def getTwitterStats(user_profile):
    twuser_limit = user_profile.twitterUsersToHarvestLimit
    hashtag_limit = user_profile.twitterHashtagsToHarvestLimit
    # collected_tweets = (Tweet.objects.filter(user__harvested_by__user__userProfile=user_profile) |
    #                     Tweet.objects.filter(hashtags__harvested_by__user__userProfile=user_profile)).count()

    twitter_user_usage = user_profile.twitterUsersToHarvest().count()
    # most_active_twitter_user = user_profile.twitterUsersToHarvest() \
    #     .annotate(harvested_count=Count('tweets')) \
    #     .order_by("-harvested_count") \
    #     .first()

    twitter_user_percent = 0
    if twuser_limit > 0:
        twitter_user_percent = twitter_user_usage * 100 / twuser_limit
    else:
        twuser_limit = 'inf'

    twitter_hashtag_percent = 0
    twitter_hashtag_usage = user_profile.twitterHashtagsToHarvest().count()
    if hashtag_limit > 0:
        twitter_hashtag_percent = twitter_hashtag_usage * 100 / hashtag_limit
    else:
        hashtag_limit = 'inf'

    # most_active_hashtag = user_profile.twitterHashtagsToHarvest() \
    #     .annotate(harvested_count=Count('tweets')) \
    #     .order_by("-harvested_count").first()
    return {
        'twitterUserUsage': twitter_user_usage,
        'twitterUserLimit': twuser_limit,
        'twitterUserPercent': twitter_user_percent,
        'twitterHashtagUsage': twitter_hashtag_usage,
        'twitterHashtagLimit': hashtag_limit,
        'twitterHashtagPercent': twitter_hashtag_percent,
        # 'collectedTweets': collected_tweets,
        # 'mostActiveTwitterUser': most_active_twitter_user,
        # 'mostActiveHashtag': most_active_hashtag,
    }


def getYoutubeStats(user_profile):
    yt_channel_usage = user_profile.ytChannelsToHarvest().count()
    yt_channel_limit = user_profile.ytChannelsToHarvestLimit
    yt_channel_percent = 0
    if yt_channel_limit:
        yt_channel_percent = yt_channel_usage * 100 / yt_channel_limit
    else:
        yt_channel_limit = 'inf'

    yt_playlist_usage = user_profile.ytPlaylistsToHarvest().count()
    yt_playlist_limit = user_profile.ytPlaylistsToHarvestLimit
    yt_playlist_percent = 0
    if yt_playlist_limit:
        yt_playlist_percent = yt_playlist_usage * 100 / yt_playlist_limit
    else:
        yt_playlist_limit = 'inf'

    collected_yt_vids = YTVideo.objects.filter(channel__harvested_by__user=user_profile.user).count()
    collected_yt_comments = YTChannel.objects \
        .filter(harvested_by__user=user_profile.user) \
        .aggregate(count=Count('comments'))['count']

    most_active_channel = user_profile.ytChannelsToHarvest() \
        .annotate(vidCount=Count('videos')) \
        .order_by('vidCount') \
        .first()

    most_active_yt_vid = YTVideo.objects \
        .filter(channel__harvested_by__user=user_profile.user) \
        .order_by('-comment_count') \
        .first()

    return {
        'ytChannelUsage': yt_channel_usage,
        'ytChannelLimit': yt_channel_limit,
        'ytChannelPercent': yt_channel_percent,
        'ytPlaylistUsage': yt_playlist_usage,
        'ytPlaylistLimit': yt_playlist_limit,
        'ytPlaylistPercent': yt_playlist_percent,
        'collectedYtVids': collected_yt_vids,
        'collectedYtComments': collected_yt_comments,
        'mostActiveChannel': most_active_channel,
        'mostActiveYtVid': most_active_yt_vid,
    }


def getFacebookStats(user_profile):
    fb_page_usage = user_profile.facebookPagesToHarvest().count()
    fb_page_limit = user_profile.facebookPagesToHarvestLimit
    fb_page_usage_percent = 0
    if fb_page_limit:
        fb_page_usage_percent = fb_page_usage * 100 / fb_page_limit
    else:
        fb_page_limit = 'inf'

    collected_f_b_statuses = FBPost.objects \
        .filter(from_profile__fbPage__isnull=False) \
        .filter(from_profile__fbPage__harvested_by__user=user_profile.user).count()

    collected_f_bcomments = FBPage.objects \
        .filter(harvested_by__user=user_profile.user) \
        .aggregate(count=Count('fbProfile__posted_comments'))['count']

    most_active_page = user_profile.facebookPagesToHarvest() \
        .annotate(statusCount=Count('fbProfile__postedStatuses')) \
        .order_by('statusCount') \
        .first()

    most_active_status = FBPost.objects \
        .filter(from_profile__fbPage__isnull=False) \
        .filter(from_profile__fbPage__harvested_by__user=user_profile.user) \
        .order_by('-comment_count') \
        .first()

    return {
        'fbPageUsage': fb_page_usage,
        'fbPageLimit': fb_page_limit,
        'fbPageUsagePercent': fb_page_usage_percent,
        'collectedFBStatuses': collected_f_b_statuses,
        'collectedFBcomments': collected_f_bcomments,
        'mostActivePage': most_active_page,
        'mostActiveStatus': most_active_status,
    }


def userLoginPage(request):
    context = {
        'user': request.user,
        'navigator': [
            ('Enregistrement', '#')
        ]
    }
    return render(request, 'AspiraUser/login_page.html', context=context)


@login_required()
def userSettings(request):
    context = {
        'user': request.user,
        "navigator": [
            ("Paramètres", "/settings"),
        ],
        "fbAccessToken": '',
    }
    if hasattr(request.user.userProfile, 'fbAccessToken') and \
            request.user.userProfile.fbAccessToken._token:
        context['fbAccessToken'] = request.user.userProfile.fbAccessToken._token
    return render(request, 'AspiraUser/settings.html', context)


def resetPWPage(request, token):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    profile = UserProfile.objects.filter(passwordResetToken__exact=token).first()
    if not profile:
        raise Http404

    if profile.passwordResetDateLimit < datetime.utcnow().replace(second=0, microsecond=0, tzinfo=utc):
        raise Http404

    if 'pass1' in request.POST and 'pass2' in request.POST:
        return resetPWConfirm(request, profile)

    return render(request, "AspiraUser/reset_pw_page.html", {
        "navigator": [
            ("Réinitialisation du mot de passe", "#"),
        ],
        'token': token,
    })


@login_required()
def search(request):
    resetUserSelection(request)
    terms = []
    query = ""
    if "query" in request.GET:
        query = request.GET['query']
    terms = digestQuery(query)
    return render(request, "AspiraUser/search_results.html", {
        'user': request.user,
        "navigator": [
            ("Recherche: \"%s\"" % "\"+\"".join(terms), "#"),
        ],
        "query": cleanQuery(query),
    })


def resetPWConfirm(request, profile):
    user = profile.user

    if user.check_password(request.POST['pass1']):
        return jsonErrors('Le nouveau mot de passe doit être différent du mot de passe actuel')

    if len(request.POST['pass1']) < 6:
        return jsonErrors('Le mot de passe doit contenir au moins 6 caractères.')

    if request.POST['pass1'] != request.POST['pass2']:
        return jsonErrors('Les mots de passe de concordent pas.')

    try:
        user.set_password(request.POST['pass1'])
        user.save()
        profile.passwordResetToken = None
        profile.passwordResetDateLimit = None
        profile.save()
    except Exception as e:
        return jResponse({'status': 'error',
                          'errors': [str(e)]})

    return jResponse({'status': 'ok'})
