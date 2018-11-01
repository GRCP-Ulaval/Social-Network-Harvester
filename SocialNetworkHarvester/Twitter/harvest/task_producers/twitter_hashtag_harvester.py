from AspiraUser.models import UserProfile, ItemHarvester
from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.tasks import harvest_twitter_user, harvest_twitter_hashtag
from Twitter.models import TWUser, Hashtag


class TwitterHashtagHarvester(BaseTaskProducer):
    batch_size = 1
    name = 'Twitter Hashtag Harvester'

    def generate_tasks(self):
        twitter_hashtag_harvesters = _get_twitter_hashtag_list()

        for twitter_hashtag in twitter_hashtag_harvesters:
            yield harvest_twitter_hashtag, [twitter_hashtag]


def _get_twitter_hashtag_list():
    profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
    twitter_hashtag_harvesters = ItemHarvester.objects.none()
    for profile in profiles:
        twitter_hashtag_harvesters = twitter_hashtag_harvesters | profile.user.harvested_items \
            .filter(twitter_hashtag__isnull=False, harvest_completed=False)
    return twitter_hashtag_harvesters
