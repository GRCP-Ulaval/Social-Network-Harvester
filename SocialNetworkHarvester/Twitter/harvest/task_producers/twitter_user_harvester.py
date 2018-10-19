from AspiraUser.models import UserProfile
from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.utils import order_queryset
from Twitter.models import TWUser


def _get_twitter_user_list():
    profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
    twitter_users = TWUser.objects.none()
    for profile in profiles:
        twitter_users = twitter_users | profile.twitterUsersToHarvest.filter(_error_on_harvest=False, protected=False)
    return order_queryset(twitter_users, '_last_tweet_harvested', delay=1)


class TwitterUserHarvester(BaseTaskProducer):
    batch_size = 100
    name = 'Twitter Users Harvest'

    def generate_tasks(self):
        twitter_users = _get_twitter_user_list()
