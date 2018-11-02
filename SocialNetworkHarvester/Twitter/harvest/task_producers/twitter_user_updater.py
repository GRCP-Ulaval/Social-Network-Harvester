from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.utils import order_queryset
from SocialNetworkHarvester.loggers.jobsLogger import log
from Twitter.harvest.tasks import update_twitter_users
from Twitter.models import TWUser


class TwitterUserUpdater(BaseTaskProducer):
    batch_size = 100
    name = 'Twitter Users Updater'

    def generate_tasks(self):
        priority_updates = order_queryset(
            TWUser.objects.filter(harvested_by__isnull=False, _error_on_update=False),
            '_last_updated',
            delay=0.5
        )

        all_users_to_update = order_queryset(
            TWUser.objects.filter(_error_on_update=False).exclude(pk__in=priority_updates),
            '_last_updated',
            delay=5
        )



        for index in range(0, priority_updates.count(), self.batch_size):
            if priority_updates[index: index + self.batch_size]:
                yield update_twitter_users, [priority_updates[index: index + self.batch_size - 1]]

        for index in range(0, all_users_to_update.count(), self.batch_size):
            if all_users_to_update[index: index + self.batch_size]:
                yield update_twitter_users, [all_users_to_update[index: index + self.batch_size - 1]]
