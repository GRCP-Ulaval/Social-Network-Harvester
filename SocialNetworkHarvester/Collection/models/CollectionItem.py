from django.db import models

from Facebook.models import FBPage
from SocialNetworkHarvester.models import nullable
from Twitter.models import TWUser, HashtagHarvester
from Youtube.models import YTChannel, YTPlaylist
from .Collection import Collection


class CollectionItem(models.Model):
    collection = models.ForeignKey(
        Collection,
        related_name='items',
        on_delete=models.PROTECT
    )
    twitter_user = models.ForeignKey(
        TWUser,
        related_name='collections_included_in',
        **nullable,
        on_delete=models.PROTECT
    )
    twitter_hashtag = models.ForeignKey(
        HashtagHarvester,
        related_name='collections_included_in',
        **nullable,
        on_delete=models.PROTECT
    )
    facebook_page = models.ForeignKey(
        FBPage,
        related_name='collections_included_in',
        **nullable,
        on_delete=models.PROTECT
    )
    youtube_channel = models.ForeignKey(
        YTChannel,
        related_name='collections_included_in',
        **nullable,
        on_delete=models.PROTECT
    )
    youtube_playlist = models.ForeignKey(
        YTPlaylist,
        related_name='collections_included_in',
        **nullable,
        on_delete=models.PROTECT
    )

    def clean(self):
        if sum([
            self.twitter_hashtag,
            self.twitter_user,
            self.facebook_page,
            self.youtube_channel,
            self.youtube_playlist
        ]) != 1:
            raise Exception('A CollectionItem must have exactly one attribute set in ['
                            'twitter_hashtag, twitter_user, facebook_page, '
                            'youtube_channel, youtube_playlist]')

    def __str__(self):
        for attr in [
            self.twitter_hashtag,
            self.twitter_user,
            self.facebook_page,
            self.youtube_channel,
            self.youtube_playlist
        ]:
            if attr:
                return str(attr)

    def object_class(self):
        for attr in [
            self.twitter_hashtag,
            self.twitter_user,
            self.facebook_page,
            self.youtube_channel,
            self.youtube_playlist
        ]:
            if attr:
                return attr.model.__name__

    def get_link(self):
        return 'link'
