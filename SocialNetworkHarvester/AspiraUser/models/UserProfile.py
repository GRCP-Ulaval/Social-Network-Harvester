from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string

from Facebook.models import FBPage
from Twitter.models import Hashtag, TWUser
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
    twitterUsersToHarvestLimit = models.IntegerField(default=30, blank=True)
    twitterHashtagsToHarvestLimit = models.IntegerField(default=5, blank=True)

    facebookApp_parameters_error = models.BooleanField(default=False)
    facebookPagesToHarvestLimit = models.IntegerField(default=20, blank=True)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)
    youtubeApp_parameters_error = models.BooleanField(default=False)
    ytChannelsToHarvestLimit = models.IntegerField(default=100, blank=True)
    ytPlaylistsToHarvestLimit = models.IntegerField(default=5, blank=True)

    passwordResetToken = models.CharField(max_length=255, null=True, blank=True, unique=True)
    passwordResetDateLimit = models.DateTimeField(null=True)

    def twitter_app_valid(self):
        return not self.twitterApp_parameters_error

    def facebook_app_valid(self):
        return not self.facebookApp_parameters_error

    def youtube_app_valid(self):
        return not self.youtubeApp_parameters_error

    def twitterUsersToHarvest(self):
        return TWUser.objects.filter(harvested_by__user=self.user)

    def twitterHashtagsToHarvest(self):
        return Hashtag.objects.filter(harvested_by__user=self.user)

    def facebookPagesToHarvest(self):
        return FBPage.objects.filter(harvested_by__user=self.user)

    def ytChannelsToHarvest(self):
        return YTChannel.objects.filter(harvested_by__user=self.user)

    def ytPlaylistsToHarvest(self):
        return YTPlaylist.objects.filter(harvested_by__user=self.user)

    def get_harvest_limit(self, model):
        return {
            TWUser: self.twitterUsersToHarvestLimit,
            Hashtag: self.twitterHashtagsToHarvestLimit,
            FBPage: self.facebookPagesToHarvestLimit,
            YTChannel: self.ytChannelsToHarvestLimit,
            YTPlaylist: self.ytPlaylistsToHarvestLimit
        }[model]

    @staticmethod
    def getUniquePasswordResetToken():
        token = get_random_string(length=254)
        while UserProfile.objects.filter(passwordResetToken=token).exists():
            token = get_random_string(length=254)
        return token

    def get_harvest_queryset(self, model):
        return {
            TWUser: self.twitterUsersToHarvest(),
            Hashtag: self.twitterHashtagsToHarvest(),
            FBPage: self.facebookPagesToHarvest(),
            YTChannel: self.ytChannelsToHarvest(),
            YTPlaylist: self.ytPlaylistsToHarvest(),
        }[model]

    def item_is_in_list(self, item):
        if isinstance(item, TWUser):
            return self.user.harvested_items.filter(twitter_user=item).exists()
        elif isinstance(item, Hashtag):
            return self.user.harvested_items.filter(twitter_hashtag=item).exists()
        elif isinstance(item, FBPage):
            return self.user.harvested_items.filter(facebook_page=item).exists()
        elif isinstance(item, YTChannel):
            return self.user.harvested_items.filter(youtube_channel=item).exists()
        elif isinstance(item, YTPlaylist):
            return self.user.harvested_items.filter(youtube_playlist=item).exists()
        else:
            raise Exception('Invalid item instance: "{}"'.format(item.__class__))

    def get_item_harvester(self, item):
        if isinstance(item, TWUser):
            return self.user.harvested_items.filter(twitter_user=item).first()
        elif isinstance(item, Hashtag):
            return self.user.harvested_items.filter(twitter_hashtag=item).first()
        elif isinstance(item, FBPage):
            return self.user.harvested_items.filter(facebook_page=item).first()
        elif isinstance(item, YTChannel):
            return self.user.harvested_items.filter(youtube_channel=item).first()
        elif isinstance(item, YTPlaylist):
            return self.user.harvested_items.filter(youtube_playlist=item).first()
        else:
            raise Exception('Invalid item instance: "{}"'.format(item.__class__))

    def remove_item_from_harvest_list(self, item):
        self.get_item_harvester(item).delete()
