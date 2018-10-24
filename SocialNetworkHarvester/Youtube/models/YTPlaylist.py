from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from SocialNetworkHarvester.utils import today
from .YTChannel import YTChannel
from .YTVideo import YTVideo


class YTPlaylist(models.Model):
    channel = models.ForeignKey(YTChannel, related_name='playlists', null=True, on_delete=models.PROTECT)
    _ident = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=256, null=True)
    description = models.CharField(max_length=4096, null=True)
    publishedAt = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    privacy_status = models.CharField(max_length=32, null=True)
    video_count = models.IntegerField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _last_video_harvested = models.DateTimeField(null=True)
    _error_on_harvest = models.BooleanField(default=False)

    def last_updated(self):
        return self._last_updated

    def error_on_update(self):
        return self._error_on_update

    def last_video_harvested(self):
        return self._last_video_harvested

    def error_on_harvest(self):
        return self._error_on_harvest

    def ident(self):
        return self._ident

    class Meta:
        app_label = "Youtube"
        verbose_name = 'Playlist Youtube'
        verbose_name_plural = 'Playlists Youtube'

    def __str__(self):
        if self.title:
            return "Playlist ('%s%s')" % (self.title[:50], "..." if len(self.title) > 50 else "")
        if self.channel:
            return "%s's playlist" % self.channel
        else:
            return "Liste de lecture non-identifiée"

    def videos(self):
        ids = self.items.values_list('video', flat=True)
        return YTVideo.objects.filter(pk__in=ids)

    def videoCount(self):
        return self.items.count()

    def get_embedded(self):
        if not self.videos().first():
            return ""
        return '<iframe width="100%" height="172px" src="https://www.youtube.com/embed/' + self.videos().first(

        )._ident + \
               '?list=' + self._ident + ' "frameborder="0" allowFullScreen></iframe>'

    def get_fields_description(self):
        return {
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique de la playlist',
                "type": "long_string",
            },
            'channel': {
                'name': 'Chaîne',
                'description': 'Chaîne sur laquelle la playlist est présentée',
                "type": "object",
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre donné à la playlist',
                "type": "short_string",
                "searchable": True,
            },
            'description': {
                'name': 'Description',
                'description': 'Description du contenu de la playlist',
                "type": "long_string",
                "searchable": True,
            },
            'publishedAt': {
                'name': 'Publication',
                'description': 'Date de publication de la playlist',
                "type": "date",
            },
            'deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle la playlist a été supprimée, si applicable',
                "type": "date",
            },
            'privacy_status': {
                'name': 'Status de confidentialité',
                'description': 'Niveau de confidentialité de la playlist (public, private, hidden, etc)',
                "type": "short_string",
            },
            "get_embedded": {
                "name": "Playlist",
                "description": "Playlist hébergée sur Youtube",
                "type": "embedded_content",
                "options": {
                    "downloadable": False,
                    "tile_style": {"height": 2, "width": 3, 'scrollable': False,
                                   'show_field_name': False, "paddingless": True,
                                   'position': 0},
                }
            },
            "_last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {"admin_only": True},
            },
            "_error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {"admin_only": True},
            },
            "_last_video_harvested": {
                "name": "Last video-harvested",
                "type": "date",
                "options": {"admin_only": True},
            },
            "_error_on_harvest": {
                "name": "Error on harvest",
                "type": "boolean",
                "options": {"admin_only": True},
            },
        }

    def get_obj_ident(self):
        return "YTPlaylist__%s" % self.pk

    def navigation_context(self):
        if self.channel:
            navigation = self.channel.navigation_context()
        else:
            navigation = [("Youtube", "/youtube")]
        navigation.append(("Liste de lecture: %" % self.title), "/youtube/playlist/%s" % self._ident)
        return navigation

    def ident(self):
        return self._ident

    def update(self, jObject):
        self.title = jObject['snippet']['title']
        self.description = jObject['snippet']['description']
        publishedAt = datetime.strptime(jObject['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        publishedAt = publishedAt.replace(tzinfo=utc)
        self.publishedAt = publishedAt
        self.privacy_status = jObject['status']['privacyStatus']
        self._last_updated = today()
        self.video_count = self.videoCount()
        self.save()

    def getLink(self):
        return '/youtube/playlist/%s' % self.pk
