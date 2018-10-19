import tweepy

from AspiraUser.models import UserProfile
from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.utils import MailReportableException
from SocialNetworkHarvester.loggers.jobsLogger import log, logError
from Twitter.harvest.client import Client
from Twitter.harvest.globals import clients_queue


def get_client_list(profiles):
    client_list = []
    for profile in profiles:
        client = create_twitter_client(profile)
        if client:
            client_list.append(client)
    return client_list


def create_twitter_client(profile):
    try:
        client = Client(
            name="%s's Twitter app" % profile.user,
            ck=profile.twitterApp_consumerKey,
            cs=profile.twitterApp_consumer_secret,
            atk=profile.twitterApp_access_token_key,
            ats=profile.twitterApp_access_token_secret,
        )
        return client
    except tweepy.error.TweepError:
        profile.twitterApp_parameters_error = True
        profile.save()
        logError('%s has got an invalid Twitter app' % profile.user)
        return None


def clear_twitter_client_queue():
    while not clients_queue.empty():
        clients_queue.get()


class TwitterClientsGenerator(BaseTaskProducer):
    name = 'TwitterClientsUpdater'

    def generate_tasks(self):
        """
        This method does not generate tasks. It filters the current twitter clients
        and updates the clients_queue continuously.
        """
        all_profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
        clients_list = get_client_list(all_profiles)
        all_profiles = all_profiles.filter(
            twitterApp_parameters_error=False)  # 2 times insures the Twitter app is valid

        if len(all_profiles) == 0:
            log('No valid Twitter client exists!')
            for profile in UserProfile.objects.all():
                profile.twitterApp_parameters_error = False
                profile.save()
            raise MailReportableException(
                'Twitter harvest has not launched',
                'No valid Twitter client exists! (reseting them all)'
            )
        clients_queue.maxsize = len(clients_list)
        log('Valid Twitter clients: %s' % [str(client) for client in clients_list])
        for client in clients_list:
            clients_queue.put(client)

        yield None
