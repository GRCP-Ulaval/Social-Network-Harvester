from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string

from Facebook.models import FBPage
from Twitter.models import TWUser, HashtagHarvester
from Youtube.models import YTChannel, YTPlaylist


class UserProfile(models.Model):
    class Meta:
        app_label = "AspiraUser"

    def __str__(self):
        return "%s's user profile" % self.user

    user = models.OneToOneField(User, related_name="userProfile", null=False, on_delete=models.CASCADE)

    twitterApp_consumerKey = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_consumer_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_key = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_parameters_error = models.BooleanField(default=False)
    twitterUsersToHarvest = models.ManyToManyField(TWUser, related_name="harvested_by", blank=True)
    twitterUsersToHarvestLimit = models.IntegerField(default=30, blank=True)
    twitterHashtagsToHarvest = models.ManyToManyField(HashtagHarvester, related_name="harvested_by", blank=True)
    twitterHashtagsToHarvestLimit = models.IntegerField(default=5, blank=True)

    facebookApp_parameters_error = models.BooleanField(default=False)
    facebookPagesToHarvest = models.ManyToManyField(FBPage, related_name="harvested_by", blank=True)
    facebookPagesToHarvestLimit = models.IntegerField(default=20, blank=True)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)
    youtubeApp_parameters_error = models.BooleanField(default=False)
    ytChannelsToHarvest = models.ManyToManyField(YTChannel, related_name="harvested_by", blank=True)
    ytChannelsToHarvestLimit = models.IntegerField(default=100, blank=True)
    ytPlaylistsToHarvest = models.ManyToManyField(YTPlaylist, related_name="harvested_by", blank=True)
    ytPlaylistsToHarvestLimit = models.IntegerField(default=5, blank=True)

    passwordResetToken = models.CharField(max_length=255, null=True, blank=True, unique=True)
    passwordResetDateLimit = models.DateTimeField(null=True)

    def twitter_app_valid(self):
        return not self.twitterApp_parameters_error

    def facebook_app_valid(self):
        return not self.facebookApp_parameters_error

    def youtube_app_valid(self):
        return not self.youtubeApp_parameters_error

    @staticmethod
    def getUniquePasswordResetToken():
        token = get_random_string(length=254)
        while UserProfile.objects.filter(passwordResetToken=token).exists():
            token = get_random_string(length=254)
        return token

    @staticmethod
    def getHarvestables():
        return {
            'TWUser': 'twitterUsersToHarvest',
            'HashtagHarvester': 'twitterHashtagsToHarvest',
            'FBPage': 'facebookPagesToHarvest',
            'YTChannel': 'ytChannelsToHarvest',
            'YTPlaylist': 'ytPlaylistsToHarvest',
        }
