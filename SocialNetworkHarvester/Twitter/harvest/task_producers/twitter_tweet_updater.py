from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.utils import order_queryset
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.tasks import update_tweets
from Twitter.models import Tweet


class TwitterTweetUpdater(BaseTaskProducer):
    batch_size = 100
    name = 'Twitter Tweets Updater'

    def generate_tasks(self):

        priority_updates = order_queryset(
            Tweet.objects.filter(_error_on_update=False, _update_frequency=1, deleted_at__isnull=True),
            '_last_updated',
            delay=1
        )

        non_priority_updates = order_queryset(
            Tweet.objects
                .filter(_error_on_update=False, deleted_at__isnull=True)
                .exclude(pk__in=priority_updates),
            '_last_updated',
            delay=5
        )

        to_update_count = priority_updates.count() + non_priority_updates.count()
        if to_update_count:
            log(
                f'{to_update_count}/{Tweet.objects.all().count()} total tweets to update.'
            )

        for index in range(0, priority_updates.count(), self.batch_size):
            if priority_updates[index: index + self.batch_size]:
                yield update_tweets, [priority_updates[index: index + self.batch_size - 1]]

        for index in range(0, non_priority_updates.count(), self.batch_size):
            if non_priority_updates[index: index + self.batch_size]:
                yield update_tweets, [non_priority_updates[index: index + self.batch_size - 1]]
