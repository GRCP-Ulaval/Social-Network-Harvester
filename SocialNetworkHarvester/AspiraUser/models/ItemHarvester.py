from django.contrib.auth.models import User
from django.db import models

from Facebook.models import FBPage
from SocialNetworkHarvester.models import nullable
from SocialNetworkHarvester.utils import x_days_ago, today
from Twitter.models import TWUser, Hashtag
from Youtube.models import YTChannel, YTPlaylist


class ItemHarvester(models.Model):
    user = models.ForeignKey(
        User,
        related_name='harvested_items',
        on_delete=models.PROTECT
    )
    twitter_user = models.ForeignKey(
        TWUser,
        related_name='harvested_by',
        **nullable,
        on_delete=models.PROTECT
    )
    twitter_hashtag = models.ForeignKey(
        Hashtag,
        related_name='harvested_by',
        **nullable,
        on_delete=models.PROTECT
    )
    facebook_page = models.ForeignKey(
        FBPage,
        related_name='harvested_by',
        **nullable,
        on_delete=models.PROTECT
    )
    youtube_channel = models.ForeignKey(
        YTChannel,
        related_name='harvested_by',
        **nullable,
        on_delete=models.PROTECT
    )
    youtube_playlist = models.ForeignKey(
        YTPlaylist,
        related_name='harvested_by',
        **nullable,
        on_delete=models.PROTECT
    )
    harvest_since = models.DateTimeField(
        default=x_days_ago(30)
    )
    harvest_until = models.DateTimeField(
        default=today()
    )

    def harvest_since_str(self):
        return self.harvest_since.strftime('%Y-%m-%d')

    def harvest_until_str(self):
        return self.harvest_until.strftime('%Y-%m-%d')

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
            raise Exception('An ItemHarvester must have exactly one attribute set in ['
                            'twitter_hashtag, twitter_user, facebook_page, '
                            'youtube_channel, youtube_playlist]')

    def get_item(self):
        for attr in self.foreign_keys():
            if attr:
                return attr

    def __str__(self):
        return "%s harvested item: %s" % (self.user, self.get_item())

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
        return "ItemHarvester__%s" % self.pk

    def get_fields_description(self):
        return self.get_item().get_fields_description()

    @staticmethod
    def create(user, item, harvest_since, harvest_until):
        foreign_key = {
            TWUser: 'twitter_user',
            Hashtag: 'twitter_hashtag',
            FBPage: 'facebook_page',
            YTChannel: 'youtube_channel',
            YTPlaylist: 'youtube_playlist'
        }[item.__class__._meta.model]

        current_items = user.harvested_items.filter(**{'%s__isnull' % foreign_key: False})

        if not current_items.filter(**{foreign_key: item}).exists():
            ItemHarvester.objects.create(
                user=user,
                **{foreign_key: item},
                harvest_since=harvest_since,
                harvest_until=harvest_until
            )
