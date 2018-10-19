from django.contrib.auth.models import User
from django.db import models

from Facebook.models import FBPage
from SocialNetworkHarvester.models import nullable
from Twitter.models import TWUser, HashtagHarvester
from Youtube.models import YTChannel, YTPlaylist


class ItemHarvester(models.Model):
    user = models.ForeignKey(
        User,
        related_name='harvested_items',
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

    def foreign_keys(self):
        return [
            self.twitter_hashtag,
            self.twitter_user,
            self.facebook_page,
            self.youtube_channel,
            self.youtube_playlist
        ]

    def clean(self):
        if sum(self.foreign_keys()) != 1:
            raise Exception('A CollectionItem must have exactly one attribute set in ['
                            'twitter_hashtag, twitter_user, facebook_page, '
                            'youtube_channel, youtube_playlist]')

    def get_item(self):
        for attr in self.foreign_keys():
            if attr:
                return attr

    def __str__(self):
        return "%s item: %s" % (self.collection, self.get_item())

    def str(self):
        item = self.get_item()
        if hasattr(item, 'str'):
            return item.str()
        return str(item)

    def object_class(self):
        return self.get_item()._meta.verbose_name

    def getLink(self):
        return self.get_item().getLink()

    def get_obj_ident(self):
        return "CollectionItem__%s" % self.pk

    def get_fields_description(self):
        return self.get_item().get_fields_description()

    @staticmethod
    def create(collection, item):
        foreign_key = {
            TWUser: 'twitter_user',
            HashtagHarvester: 'twitter_hashtag',
            FBPage: 'facebook_page',
            YTChannel: 'youtube_channel',
            YTPlaylist: 'youtube_playlist'
        }[item.__class__._meta.model]

        current_items = collection.collection_items.filter(**{'%s__isnull' % foreign_key: False})

        if not current_items.filter(**{foreign_key: item}).exists():
            CollectionItem.objects.create(
                collection=collection,
                **{foreign_key: item}
            )
