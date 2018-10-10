from django.contrib.auth.models import User
from django.db import models

from SocialNetworkHarvester.loggers.viewsLogger import log
from SocialNetworkHarvester.models import djangoNow


class Collection(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True
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

    def items_twitter_users(self):
        return self.collection_items.filter(twitter_user__isnull=False)

    def items_hashtag_harvesters(self):
        items = self.collection_items.filter(twitter_hashtag__isnull=False)
        return items
        return self.collection_items.filter(twitter_hashtag__isnull=False)

    def items_facebook_pages(self):
        return self.collection_items.filter(facebook_page__isnull=False)

    def items_youtube_channels(self):
        return self.collection_items.filter(youtube_channel__isnull=False)

    def items_youtube_playlists(self):
        return self.collection_items.filter(youtube_playlist__isnull=False)

    def __str__(self):
        return 'Collecte "%s"' % (self.name)

    def serialize(self, fields=None):
        return {
            'id': self.pk,
            'name': self.name,
            'description': self.description,
            'created_on': self.created_on.strftime('%Y-%m-%d'),
            'created_by': {
                'first_name': self.created_by.first_name,
                'last_name': self.created_by.last_name
            },
            'harvest_is_active': self.harvest_is_active,
            'harvest_start': self.harvest_start.strftime('%Y-%m-%d'),
            'harvest_end': self.harvest_end.strftime('%Y-%m-%d'),
            'all_curators': [
                {
                    'first_name': curator.first_name,
                    'last_name': curator.last_name
                } for curator in self.curators.all()
            ],
            'all_followers': [
                {
                    'first_name': follower.first_name,
                    'last_name': follower.last_name
                } for follower in self.followers.all()
            ]
        }


class InvalidFieldException(Exception):
    pass
