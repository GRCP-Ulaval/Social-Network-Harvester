import tweepy

from SocialNetworkHarvester.harvest.globals import tasks_queue
from SocialNetworkHarvester.harvest.utils import today, check_stop_flag_raised
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.client import get_client, return_client


def update_twitter_users(twitter_user_batch):
    twitter_user_batch = list(twitter_user_batch)
    client = get_client('lookup_users')
    try:
        responses = client.call('lookup_users', user_ids=[user._ident for user in twitter_user_batch])
    except tweepy.error.TweepError:
        log('got tweepy.error.TweepError!')
        log('user_ids = %s' % [user._ident for user in twitter_user_batch])
        return_client(client)
        raise
    return_client(client)

    for response in responses:
        check_stop_flag_raised()
        tw_user = next((user for user in twitter_user_batch if user._ident == response._json['id']), None)
        if tw_user:
            tasks_queue.put((
                update_twitter_user_from_response,
                [tw_user, response._json],
                {}
            ))
            twitter_user_batch.remove(tw_user)
    for tw_user in twitter_user_batch:
        log('Twitter user (%s) has returned no result.' % tw_user)
        # twUser._error_on_update = True
        tw_user._last_updated = today()
        tw_user._update_frequency = 5
        tw_user.save()


def update_twitter_user_from_response(twitter_user, response):
    twitter_user.UpdateFromResponse(response)
    #log('updated %s' % twitter_user)
    if twitter_user.harvested_by.count():
        twitter_user._update_frequency = 1
    else:
        twitter_user._update_frequency = 5
    twitter_user.save()
