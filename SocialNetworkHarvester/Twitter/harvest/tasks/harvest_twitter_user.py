from django.utils.timezone import utc

from SocialNetworkHarvester.harvest.globals import global_task_queue
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.client import CustomCursor
from Twitter.harvest.tasks.update_tweets import update_tweet_from_response


def harvest_twitter_user(twitter_user_harvester):
    twitter_user = twitter_user_harvester.twitter_user
    cursor = CustomCursor(
        'user_timeline',
        id=twitter_user._ident,
        count=200
    )
    log(
        f'harvesting {twitter_user} tweets from '
        f'{twitter_user_harvester.harvest_since.strftime("%Y-%m-%d")} to '
        f'{twitter_user_harvester.harvest_until.strftime("%Y-%m-%d")}'
    )
    none_received_count = 0
    while True:
        tweet = cursor.next()
        if not tweet:
            none_received_count += 1
            if none_received_count > 10:
                break
            continue
        else:
            none_received_count = 0

        log(tweet.created_at)
        created_at = tweet.created_at.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
        if created_at <= twitter_user_harvester.harvest_until:
            global_task_queue.add(update_tweet_from_response, [tweet])

        if created_at < twitter_user_harvester.harvest_since:
            break
    log(f'Tweet-harvest completed for {twitter_user_harvester}')
    twitter_user_harvester.harvest_completed = True
    twitter_user_harvester.save()
