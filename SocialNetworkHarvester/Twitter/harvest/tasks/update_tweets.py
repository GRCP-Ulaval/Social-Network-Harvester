import tweepy

from SocialNetworkHarvester.harvest.utils import check_stop_flag_raised, add_task
from SocialNetworkHarvester.loggers.jobsLogger import log
from SocialNetworkHarvester.utils import today
from Twitter.harvest.client import get_client, return_client
from Twitter.models import Tweet


def update_tweets(tweet_batch):
    if not tweet_batch.count():
        return

    tweet_batch = list(tweet_batch)
    client = get_client('statuses_lookup')
    try:
        responses = client.call('statuses_lookup', id_=[tweet._ident for tweet in tweet_batch], trim_user=True)
    except tweepy.error.TweepError:
        log('got tweepy.error.TweepError!')
        log('tweet ids = %s' % [tweet._ident for tweet in tweet_batch])
        return_client(client)
        raise
    return_client(client)

    for response in responses:
        check_stop_flag_raised()
        tweet = next((tweet for tweet in tweet_batch if tweet._ident == response._json['id']), None)
        if tweet:
            add_task(update_tweet_from_response, args=[response])
            tweet_batch.remove(tweet)

    for tweet in tweet_batch:
        log('%s has been deleted' % tweet)
        tweet.deleted_at = today()
        tweet.save()


def update_tweet_from_response(tweet_response):
    # log(f'{tweet_response.author.screen_name}: {tweet_response.created_at}')
    tweet, new = Tweet.objects.get_or_create(_ident=tweet_response.id)
    tweet.UpdateFromResponse(tweet_response._json)

    if tweet.user.harvested_by:
        tweet._update_frequency = 1
    else:
        tweet._update_frequency = 5
