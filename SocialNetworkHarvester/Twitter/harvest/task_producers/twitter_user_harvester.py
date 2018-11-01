from AspiraUser.models import UserProfile, ItemHarvester
from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.tasks import harvest_twitter_user
from Twitter.models import TWUser


class TwitterUserHarvester(BaseTaskProducer):
    batch_size = 100
    name = 'Twitter Users Harvester'

    def generate_tasks(self):
        twitter_user_harvesters = _get_twitter_user_list()

        twitter_user_harvesters_count = twitter_user_harvesters.count()
        if twitter_user_harvesters_count:
            log(
                f"{twitter_user_harvesters_count}/"
                f"{ItemHarvester.objects.filter(twitter_user__isnull=False).count()} "
                f"Twitter users to tweet-harvest"
            )

        for twitter_user in twitter_user_harvesters:
            yield harvest_twitter_user, [twitter_user]


def _get_twitter_user_list():
    profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
    twitter_users_harvester = ItemHarvester.objects.none()
    for profile in profiles:
        twitter_users_harvester = twitter_users_harvester | profile.user.harvested_items \
            .filter(twitter_user__isnull=False, harvest_completed=False) \
            .filter(twitter_user___error_on_harvest=False)
    return twitter_users_harvester
