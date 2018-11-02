from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, render_to_response, get_object_or_404

from AspiraUser.models import resetUserSelection
from SocialNetworkHarvester.loggers.viewsLogger import log
from Twitter.models import TWUser, Hashtag, Tweet


@login_required()
def twitterBaseView(request):
    context = {
        'user': request.user,
        "navigator": [
            ("Twitter", "/twitter"),
        ]
    }
    log(context)
    resetUserSelection(request)
    return render(request, 'Twitter/TwitterBase.html', context)


@login_required()
def twUserView(request, TWUser_value):
    twUser = get_object_or_404(TWUser, pk=TWUser_value)
    context = {
        'user': request.user,
        'twUser': twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/{}".format(twUser.pk)),
        ],
    }
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        try:
            return render_to_response('Twitter/TwitterUserSnip.html', context)
        except:
            pass
    else:
        resetUserSelection(request)
        return render(request, 'Twitter/TwitterUser.html', context)


@login_required()
def twHashtagView(request, TWHashtagTerm):
    hashtag = None
    try:
        hashtag = Hashtag.objects.get(pk=TWHashtagTerm)
    except:
        try:
            hashtag = Hashtag.objects.get(term=TWHashtagTerm)
        except:
            raise Http404('No hashtag matches that value')
    context = {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            ("#%s" % hashtag.term, ""),
        ],
    }
    resetUserSelection(request)
    return render(request, 'Twitter/TwitterHashtag.html', context)


def twTweetView(request, tweetId):
    tweet = None
    try:
        tweet = Tweet.objects.get(pk=tweetId)
    except:
        pass
    if not tweet:
        tweet = Tweet.objects.get(_ident=tweetId)
    if not tweet:
        raise Http404('No tweet matches that value')
    twUser = tweet.user
    context = {
        'user': request.user,
        'tweet': tweet,
        'navigator': [
            ("Twitter", "/twitter"),
            ((str(twUser) if twUser else 'Unidentifed TWUser'),
             ("/twitter/user/" + str(twUser.pk) if twUser else '#')),
            ("Tweet", ""),
        ],
    }
    resetUserSelection(request)
    return render(request, 'Twitter/TwitterTweet.html', context)
