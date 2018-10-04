from django.contrib.auth.models import User
from django.db import models

from Facebook.models import FBPage
from SocialNetworkHarvester.models import djangoNow
from Twitter.models import TWUser, HashtagHarvester
from Youtube.models import YTChannel, YTPlaylist


class Collection(models.Model):
    name = models.CharField(
        max_length=512,
    )
    description = models.TextField(
        null=True,
    )
    created_on = models.DateTimeField(
        default=djangoNow
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_collections',
        null=True,
        blank=True
    )
    harvest_is_active = models.BooleanField(
        default=False
    )
    harvest_start = models.DateTimeField()
    harvest_end = models.DateTimeField()
    curators = models.ManyToManyField(
        User,
        related_name='curated_collections'
    )
    followers = models.ManyToManyField(
        User,
        related_name='followed_collections'
    )
    twitter_users = models.ManyToManyField(
        TWUser,
        related_name='collections_included_in'
    )
    twitter_hashtags = models.ManyToManyField(
        HashtagHarvester,
        related_name='collections_included_in'
    )
    facebook_pages = models.ManyToManyField(
        FBPage,
        related_name='collections_included_in'
    )
    youtube_channels = models.ManyToManyField(
        YTChannel,
        related_name='collections_included_in'
    )
    youtube_playlists = models.ManyToManyField(
        YTPlaylist,
        related_name='collections_included_in'
    )
