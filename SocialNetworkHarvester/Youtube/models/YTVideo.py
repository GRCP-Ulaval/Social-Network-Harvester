import re
from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from SocialNetworkHarvester.utils import today
from .YTChannel import YTChannel


class YTVideo(models.Model):
    # basic fields
    _ident = models.CharField(max_length=128, unique=True)
    channel = models.ForeignKey(YTChannel, related_name='videos', null=True, on_delete=models.PROTECT)
    publishedAt = models.DateTimeField(null=True)
    title = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=8192, null=True)
    contentRating_raw = models.CharField(max_length=2048, null=True)
    privacyStatus = models.CharField(max_length=32, null=True)
    publicStatsViewable = models.BooleanField(default=True)
    recordingLocation = models.CharField(max_length=256, null=True)
    streamStartTime = models.DateTimeField(null=True)
    streamEndTime = models.DateTimeField(null=True)
    streamConcurrentViewers = models.IntegerField(null=True)

    # statistics
    view_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    dislike_count = models.IntegerField(null=True)
    favorite_count = models.IntegerField(null=True)
    comment_count = models.IntegerField(null=True)

    # private fields
    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1)
    _file_path = models.CharField(max_length=512, null=True)

    def last_updated(self):
        return self._last_updated

    def deleted_at(self):
        return self._deleted_at

    def error_on_update(self):
        return self._error_on_update

    def update_frequency(self):
        return self._update_frequency

    def file_path(self):
        return self._file_path

    class Meta:
        app_label = "Youtube"
        verbose_name = 'Video Youtube'
        verbose_name_plural = 'Videos Youtube'

    def __str__(self):
        if self.channel:
            if self.title:
                return "%s's video (%s)" % (self.channel,
                                            self.title[:15] + "..." * (len(self.title) > 15))
            else:
                return "%s's video #%s" % (self.channel, self._ident)
        else:
            return 'video #%s' % self._ident

    def get_obj_ident(self):
        return "YTVideo__%s" % self.pk

    def ident(self):
        return self._ident

    def getLink(self):
        if not self.title:
            return None
        return "/youtube/video/%s" % self.pk

    def navigation_context(self):
        if self.channel:
            navigation = self.channel.navigation_context()
            navigation.append(("Vidéo: %s" % self.title, self.getLink()))
        return navigation

    def title_underscore(self):
        return re.sub(' ', '_', self.title)

    def embedded_video(self):
        return '<iframe width="100%" height="172px" src="https://www.youtube.com/embed/' + self._ident + \
               '?wmode=opaque" frameborder="0" allowFullScreen></iframe>'

    def get_fields_description(self):
        return {
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique de la vidéo',
                'type': 'short_string',
            },
            'description': {
                'name': 'Description',
                'description': 'Description du contenu de la vidéo',
                'type': 'long_string',
                "searchable": True,
            },
            'contentRating_raw': {
                'name': 'Évaluation du contenu',
                'description': 'Évaluation publique du contenu de la vidéo',
                'type': 'short_string',
            },
            'channel': {
                'name': 'Auteur',
                'description': 'Chaîne Youtube ayant posté la vidéo',
                'type': 'object',
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre de la vidéo',
                'type': 'long_string',
                "searchable": True,
            },
            'publicStatsViewable': {
                'name': 'Statistiques publiques',
                'description': 'Determine si l\'auteur partage publiquement les statistiques de la vidéo (nombre de '
                               'vues, nombre de commentaires, etc.)',
                'type': 'boolean',
            },
            'publishedAt': {
                'name': 'Date de publication',
                'description': 'Date de publication de la vidéo',
                'type': 'date',
            },
            'recordingLocation': {
                'name': 'Location d\'enregistrement',
                'description': 'Location à laquelle la vidéo a été créée/éditée/postée',
                'type': 'short_string',
            },
            'streamStartTime': {
                'name': 'Départ stream',
                'description': 'Si la vidéo est un livestream, temps de démarage du livestream',
                'type': 'date',
            },
            'streamEndTime': {
                'name': 'Fin stream',
                'description': 'Si la vidéo est un livestream, temps de fin du livestream',
                'type': 'date',
            },
            'streamConcurrentViewers': {
                'name': 'Vues concurentes du stream',
                'description': 'Si la vidéo est un livestream, nombre maximum de vues en simultané',
                'type': 'integer',
            },
            'comment_count': {
                'name': 'Nombre de commentaires',
                'description': 'Nombre de commentaires postés dans la section discussion (au moment de la dernière '
                               'mise à jour)',
                'type': 'integer',
            },
            'like_count': {
                'name': 'Nombre de likes',
                'description': 'Nombre de likes de la vidéo (au moment de la dernière mise à jour)',
                'type': 'integer',
            },
            'dislike_count': {
                'name': 'Nombre de dislikes',
                'description': 'Nombre de dislikes de la vidéo (au moment de la dernière mise à jour)',
                'type': 'integer',
            },
            'favorite_count': {
                'name': 'Nombre de favoris',
                'description': 'Nombre de personnes ayant ajouté la vidéo à leurs "favoris" (au moment de la dernière'
                               ' mise à jour)',
                'type': 'integer',
            },
            'view_count': {
                'name': 'Nombre de vues',
                'description': 'Nombre de vues total de la vidéo (au moment de la dernière mise à jour)',
                'type': 'integer',
            },
            '_deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle la vidéo à été supprimée (si applicable)',
                'type': 'integer',
            },
            "embedded_video": {
                "name": "Vidéo",
                "description": "Vidéo hébergée sur Youtube",
                "type": "embedded_content",
                "options": {
                    "downloadable": False,
                    "tile_style": {"height": 2, "width": 3, 'scrollable': False,
                                   'show_field_name': False, "paddingless": True,
                                   'position': 0},
                }
            },
            "_deleted_at": {
                "name": "Deleted at",
                "type": "date",
                "options": {"admin_only": True}
            },
            "_last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {"admin_only": True}
            },
            "_error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {"admin_only": True}
            },
            "_update_frequency": {
                "name": "Update frequency",
                "type": "integer",
                "options": {"admin_only": True}
            },
            "_file_path": {
                "name": "File path",
                "type": "short_string",
                "options": {"admin_only": True, }
            },
        }

    basicFields = {
        '_ident': ['id'],
        'title': ['snippet', 'title'],
        'description': ['snippet', 'description'],
        'contentRating_raw': ['contentRating'],
        'privacyStatus': ['status', 'privacyStatus'],
        'publicStatsViewable': ['status', 'publicStatsViewable'],
        'recordingLocation': ['recordingDetails', 'locationDescription'],
        'streamConcurrentViewers': ['liveStreamingDetails', 'concurrentViewers'],
        'view_count': ['statistics', 'viewCount'],
        'like_count': ['statistics', 'likeCount'],
        'dislike_count': ['statistics', 'dislikeCount'],
        'favorite_count': ['statistics', 'favoriteCount'],
        'comment_count': ['statistics', 'commentCount'],
    }
    dateTimeFields = {
        'publishedAt': ['snippet', 'publishedAt'],
        'streamStartTime': ['liveStreamingDetails', 'actualStartTime'],
        'streamEndTime': ['liveStreamingDetails', 'actualEndTime'],
    }
    statistics = {
        'view_counts': ['statistics', 'viewCount'],
        'like_counts': ['statistics', 'likeCount'],
        'dislike_counts': ['statistics', 'dislikeCount'],
        'favorite_counts': ['statistics', 'favoriteCount'],
        'comment_counts': ['statistics', 'commentCount'],
    }

    def update(self, jObject):
        assert isinstance(jObject, dict), 'jObject must be a dict or json instance!'
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateImages(jObject)
        self._last_updated = today()
        self.save()

    def copyBasicFields(self, jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    setattr(self, attr, val)

    def copyDateTimeFields(self, jObject):
        for attr in self.dateTimeFields:
            if self.dateTimeFields[attr][0] in jObject:
                val = jObject[self.dateTimeFields[attr][0]]
                for key in self.dateTimeFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
                    val = val.replace(tzinfo=utc)
                    setattr(self, attr, val)

    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    # log('Invalid dict sequence: %s. Object returned is: %s' % (self.statistics[attrName],val))
                    val = None
            if val:
                if not countObjs.exists():
                    objType.objects.create(video=self, value=val)
                elif countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(video=self, value=val)

    def updateImages(self, jObject):
        pass
