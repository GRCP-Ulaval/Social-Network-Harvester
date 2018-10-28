from django.db import models

from SocialNetworkHarvester.models import Text_time_label, time_label, Integer_time_label
from .Tweet import Tweet
from .TWUser import TWUser


################### TWUSER ####################

class screen_name(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="screen_names", on_delete=models.CASCADE)


class name(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="names", on_delete=models.CASCADE)


class time_zone(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="time_zones", on_delete=models.CASCADE)


class description(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="descriptions", on_delete=models.CASCADE)


class statuses_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="statuses_counts", on_delete=models.CASCADE)


class favourites_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="favourites_counts", on_delete=models.CASCADE)


class followers_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="followers_counts", on_delete=models.CASCADE)


class friends_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="friends_counts", on_delete=models.CASCADE)


class listed_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="listed_counts", on_delete=models.CASCADE)


class follower(time_label):
    twuser = models.ForeignKey(TWUser, related_name="followers", on_delete=models.CASCADE)
    value = models.ForeignKey(TWUser, related_name='friends',
                              on_delete=models.CASCADE)  # "value" user is following "twuser", calls it it's "friend"
    ended = models.DateTimeField(null=True)

    def get_fields_description(self):
        val = super(follower, self).get_fields_description()
        val.update({
            'ended': {
                'name': 'Terminé',
                'description': "Date à l'aquelle l'utilisateur Twitter a cessé de suivre l'utilisateur-cible"},
            'recorded_time': {
                'name': 'Temps d\'enregistrement',
                'description': 'Temps auquel la relation as été enregistrée'}
        })
        return val



############### TWEET ####################

class retweet_count(Integer_time_label):
    tweet = models.ForeignKey(Tweet, related_name="retweet_counts", on_delete=models.CASCADE)


class favorite_tweet(time_label):
    twuser = models.ForeignKey(TWUser, related_name="favorite_tweets", on_delete=models.CASCADE)
    value = models.ForeignKey(Tweet, related_name='favorited_by', on_delete=models.CASCADE)
    ended = models.DateTimeField(null=True)

    def get_fields_description(self):
        val = super(favorite_tweet, self).get_fields_description()
        val.update({
            'ended': {
                'name': 'Ended',
                'description': 'Time at wich the TWuser no longer favorites the target Tweet'
            },
            'recorded_time': {
                'name': 'Recorded Time',
                'description': 'Time at wich the target Tweet has been recorded as a favorite of the Twitter user'
            }
        })
        return val

