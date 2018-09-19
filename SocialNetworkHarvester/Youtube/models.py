from django.db import models

from SocialNetworkHarvester.models import Integer_time_label, Big_integer_time_label, Image_time_label, time_label
from SocialNetworkHarvester.settings import youtubeLogger, DEBUG

log = lambda s: youtubeLogger.log(s) if DEBUG else 0
pretty = lambda s: youtubeLogger.pretty(s) if DEBUG else 0
logerror = lambda s: youtubeLogger.exception(s)
from Youtube.management.commands.harvest.queues import *
import re

from datetime import datetime
from django.utils.timezone import utc

today = lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


####################### YTCHANNEL  #######################

class YTChannel(models.Model):
    _ident = models.CharField(max_length=128, null=True, unique=True)
    userName = models.CharField(max_length=32, null=True)
    description = models.CharField(max_length=8192, null=True)
    keywords = models.CharField(max_length=1000, null=True)
    profileColor = models.CharField(max_length=16, null=True)
    title = models.CharField(max_length=512, null=True)
    publishedAt = models.DateTimeField(null=True)
    hiddenSubscriberCount = models.BooleanField(default=False)
    isLinked = models.BooleanField(default=False)
    privacyStatus = models.CharField(max_length=32, null=True)
    featuredChannel = models.ManyToManyField('self', related_name='featured_by')
    commentCount = models.BigIntegerField(null=True)
    subscriberCount = models.BigIntegerField(null=True)
    videoCount = models.IntegerField(null=True)
    viewCount = models.BigIntegerField(null=True)

    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _last_video_harvested = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _error_on_harvest = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1)  # 1 = every day, 2 = every 2 days, etc.
    _harvest_frequency = models.IntegerField(default=1)
    _has_reached_begining = models.BooleanField(default=False)
    _error_on_comment_harvest = models.BooleanField(default=False)
    _last_comment_harvested = models.DateTimeField(null=True)
    _earliest_comment_page_token = models.CharField(max_length=512, null=True)
    _has_reached_comments_begining = models.BooleanField(default=False)
    _last_subs_harvested = models.DateTimeField(null=True)
    _public_subscriptions = models.BooleanField(default=True)
    _last_playlists_harvested = models.DateTimeField(null=True)
    _deleted_at = models.DateTimeField(null=True)

    def deleted_at(self):
        return self._deleted_at

    def last_updated(self):
        return self._last_updated

    def last_video_harvested(self):
        return self._last_video_harvested

    def error_on_update(self):
        return self._error_on_update

    def error_on_harvest(self):
        return self._error_on_harvest

    def update_frequency(self):
        return self._update_frequency

    def harvest_frequency(self):
        return self._harvest_frequency

    def has_reached_begining(self):
        return self._has_reached_begining

    def error_on_comment_harvest(self):
        return self._error_on_comment_harvest

    def last_comment_harvested(self):
        return self._last_comment_harvested

    def earliest_comment_page_token(self):
        return self._earliest_comment_page_token

    def has_reached_comments_begining(self):
        return self._has_reached_comments_begining

    def last_subs_harvested(self):
        return self._last_subs_harvested

    def public_subscriptions(self):
        return self._public_subscriptions

    def last_playlists_harvested(self):
        return self._last_playlists_harvested

    basicFields = {
        '_ident': ['id'],
        'description': ['brandingSettings', 'channel', 'description'],
        'keywords': ['brandingSettings', 'channel', 'keywords'],
        'profileColor': ['brandingSettings', 'channel', 'profileColor'],
        'title': ['brandingSettings', 'channel', 'title'],
        'isLinked': ['status', 'isLinked'],
        'privacyStatus': ['status', 'privacyStatus'],
        'hiddenSubscriberCount': ['statistics', 'hiddenSubscriberCount'],
        'commentCount': ['statistics', 'commentCount'],
        'subscriberCount': ['statistics', 'subscriberCount'],
        'videoCount': ['statistics', 'videoCount'],
        'viewCount': ['statistics', 'viewCount'],
    }
    dateTimeFields = {
        'publishedAt': ['snippet', 'publishedAt'],
    }
    statistics = {
        'comment_counts': ['statistics', 'commentCount'],
        'subscriber_counts': ['statistics', 'subscriberCount'],
        'video_counts': ['statistics', 'videoCount'],
        'view_counts': ['statistics', 'viewCount'],
    }

    class Meta:
        app_label = "Youtube"

    def __str__(self):
        if self.title: return self.title
        if self.userName: return self.userName
        if self._ident: return "channel #%s" % self._ident
        return 'Unidentified YTChannel'

    def get_fields_description(self):
        return {
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique de la chaîne',
                "type": "short_string",
            },
            'description': {
                'name': 'Description',
                'description': 'Description du type de contenu de la chaîne',
                "type": "long_string",
                "searchable": True,
            },
            'keywords': {
                'name': 'Mot-clefs',
                'description': 'Mots-clefs associés à la chaîne',
                "type": "long_string",
            },
            'profileColor': {
                'name': 'Couleur de profil',
                'description': 'Couleur de fond de la chaîne',
                "type": "short_string",
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre de la chaîne',
                "type": "short_string",
                "searchable": True,
            },
            'userName': {
                'name': 'Nom d\'utilisateur',
                'description': 'Nom unique de la chaîne. Peut être changé durant l\'existence de la chaîne. '
                               'Non-permanent',
                "type": "short_string",
                "searchable": True,
            },
            'publishedAt': {
                'name': 'Création',
                'description': 'Date de création de la chaîne',
                "type": "date",
            },
            'hiddenSubscriberCount': {
                'name': 'Nombre d\'abonnés caché',
                'description': 'Détermine si le nombre d\'abonnés à la chaine est privé ou public',
                "type": "boolean",
            },
            'isLinked': {
                'name': 'Liaison Google+',
                'description': 'Détermine si la chaîne est reliée à un compte Google+',
                "type": "boolean",
            },
            'privacyStatus': {
                'name': 'Confidentialité',
                'description': 'Status de confidentialité de la chaîne. Peut être "Private", "Public" or "Unlisted"',
                "type": "short_string",
            },
            'featuredChannel': {
                'name': 'Chaînes présentées',
                'description': 'Autres chaînes mises en vedette par la chaîne',
                "type": "object_list",
            },
            'commentCount': {
                'name': 'Nombre de commentaires',
                'description': 'Nombre de commentaires postés sur la page "discussion" de la chaîne (au moment de la '
                               'dernière mise à jour)',
                "type": "integer",
            },
            'subscriberCount': {
                'name': 'Nombre d\'abonnés',
                'description': 'Nombre d\'abonnés à la chaîne (au moment de la dernière mise à jour)',
                "type": "integer",
            },
            'videoCount': {
                'name': 'Nombre de vidéos',
                'description': 'Nombre de vidéos postés sur la chaîne (au moment de la dernière mise à jour)',
                "type": "integer",
            },
            'viewCount': {
                'name': 'Nombre de vues',
                'description': 'Nombre combiné de vues de toutes les vidéos postés par la chaîne (au moment de la '
                               'dernière mise à jour)',
                "type": "integer",
            },
            "_last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
            "_last_video_harvested": {
                "name": "Last video-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
            "_error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_error_on_harvest": {
                "name": "Error on harvest",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_update_frequency": {
                "name": "Update frequency",
                "type": "integer",
                "options": {
                    "admin_only": True
                }
            },
            "_harvest_frequency": {
                "name": "Harvest frequency",
                "type": "integer",
                "options": {
                    "admin_only": True
                }
            },
            "_has_reached_begining": {
                "name": "Has reached begining",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_error_on_comment_harvest": {
                "name": "Error on comment-harvest",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_last_comment_harvested": {
                "name": "Last comment-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
            "_earliest_comment_page_token": {
                "name": "Earliest page-token",
                "type": "short_string",
                "options": {
                    "admin_only": True
                }
            },
            "_has_reached_comments_begining": {
                "name": "Has reached comment-begining",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_last_subs_harvested": {
                "name": "Last subs-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
            "_public_subscriptions": {
                "name": "Public subscriptions",
                "type": "boolean",
                "options": {
                    "admin_only": True
                }
            },
            "_last_playlists_harvested": {
                "name": "Last playlist-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
            "_deleted_at": {
                "name": "Deleted at",
                "type": "date",
                "options": {
                    "admin_only": True
                }
            },
        }

    def get_obj_ident(self):
        return "YTChannel__%s" % self.pk

    def ident(self):
        return self._ident

    def navigation_context(self):
        return [("Youtube", "/youtube"),
                ("Chaîne: %s" % self, self.getLink())]

    def getLink(self):
        return "/youtube/channel/%s" % self.pk

    # @youtubeLogger.debug(showArgs=False)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')
        # pretty(jObject)
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateImages(jObject)
        self._last_updated = today()
        self.save()

    # @youtubeLogger.debug(showArgs=True)
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

    # @youtubeLogger.debug()
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

    # @youtubeLogger.debug()
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    pass
                    # log('Invalid dict sequence: %s'%self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(channel=self, value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(channel=self, value=val)

    # @youtubeLogger.debug()
    def updateImages(self, jObject):
        # TODO: Save a copy of the images on disk
        pass


class SubscriberCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriber_counts', on_delete=models.CASCADE)


class VideoCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='video_counts', on_delete=models.CASCADE)


class Subscription(time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriptions', on_delete=models.CASCADE)
    value = models.ForeignKey(YTChannel, related_name='subscribers', on_delete=models.CASCADE)
    ended = models.DateTimeField(null=True)


#######################  YTVIDEO  ########################

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

    # @youtubeLogger.debug()
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

    # @youtubeLogger.debug()
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

    # @youtubeLogger.debug()
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


class CommentCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='comment_counts', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='comment_counts', null=True, on_delete=models.CASCADE)


class ViewCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='view_counts', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='view_counts', null=True, on_delete=models.CASCADE)


class DislikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='dislike_counts', null=True, on_delete=models.CASCADE)


class FavoriteCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='favorite_counts', null=True, on_delete=models.CASCADE)


class ContentImage(Image_time_label):
    channel = models.ForeignKey(YTChannel, related_name='images', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='images', null=True, on_delete=models.CASCADE)


#######################  YTPLAYLIST  #####################

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
        return '<iframe width="100%" height="172px" src="https://www.youtube.com/embed/' + self.videos().first()._ident + \
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
        if not self.channel:
            self.updateChannel(jObject)
        self.title = jObject['snippet']['title']
        self.description = jObject['snippet']['description']
        publishedAt = datetime.strptime(jObject['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        publishedAt = publishedAt.replace(tzinfo=utc)
        self.publishedAt = publishedAt
        self.privacy_status = jObject['status']['privacyStatus']
        self._last_updated = today()
        self.video_count = self.videoCount()
        self.save()

    def updateChannel(self, jObject):
        channel, new = YTChannel.objects.get_or_create(_ident=jObject['snippet']['channelId'])
        if new:
            channelUpdateQueue.put(channel)
        self.channel = channel


class YTPlaylistItem(models.Model):
    playlist = models.ForeignKey(YTPlaylist, related_name='items', on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='playlistsSpots', on_delete=models.CASCADE)
    playlistOrder = models.IntegerField(null=True)

    def get_fields_description(self):
        fields = {
            'playlistOrder': {
                'name': 'Position',
                'description': 'Position de la vidéo dans la liste de lecture'
            },
        }
        videoFields = YTVideo().get_fields_description()
        for key in videoFields:
            fields['video__%s' % key] = videoFields[key]
        return fields

    def get_obj_ident(self):
        return "YTPlaylistItem__%s" % self.pk

    class Meta:
        app_label = "Youtube"


#######################  YTCOMMENT  ######################

class YTComment(models.Model):
    # basic fields
    video_target = models.ForeignKey(YTVideo, related_name='comments', null=True, on_delete=models.PROTECT)
    channel_target = models.ForeignKey(YTChannel, related_name='comments', null=True, on_delete=models.PROTECT)
    parent_comment = models.ForeignKey("self", related_name='replies', null=True, on_delete=models.PROTECT)
    author = models.ForeignKey(YTChannel, related_name='posted_comments', null=True, on_delete=models.PROTECT)
    _ident = models.CharField(max_length=128, unique=True)
    _text_max_length = 8192
    text = models.CharField(max_length=_text_max_length, null=True)
    text_truncated = models.BooleanField(default=False)
    publishedAt = models.DateTimeField(null=True)
    updatedAt = models.DateTimeField(null=True)

    # statistics
    likeCount = models.BigIntegerField(default=0)
    numberOfReplies = models.IntegerField(default=0)

    # private fields
    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=2)

    def deleted_at(self):
        return self._deleted_at

    def last_updated(self):
        return self._last_updated

    def error_on_update(self):
        return self._error_on_update

    def update_frequency(self):
        return self._update_frequency

    def get_fields_description(self):
        return {
            'video_target': {
                'name': 'Video ciblée',
                'description': 'Video Youtube à laquelle le commentaire est addressé',
                "type": "object",
            },
            'channel_target': {
                'name': 'Chaîne ciblée',
                'description': 'Chaîne Youtube à laquelle le commentaire est addressé ou chaîne ayant posté la vidéo '
                               'sous laquelle apparait le commentaire',
                "type": "object",
            },
            'parent_comment': {
                'name': 'Commentaire ciblé',
                'description': 'Commentaire auquel le commentaire est addressé',
                "type": "object",
            },
            'author': {
                'name': 'Auteur',
                'description': 'Chaîne de l\'auteur du commentaire',
                "type": "object",
            },
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique du commentaire',
                "type": "long_string",
            },
            'text': {
                'name': 'Texte',
                'description': 'Contenu textuel du commentaire',
                "type": "long_string",
                "searchable": True,
            },
            'text_truncated': {
                'name': 'Texte raccourci',
                'description': 'Détermine si le texte du commentaire a été racourci par le SNH pour pouvoir être\
                 enregistré dans la base de données. Auquel cas il est racourci à %s caratères' % (
                    self._text_max_length if self else 'N'),
                "type": "boolean",
            },
            'publishedAt': {
                'name': 'Date de publication',
                'description': 'Date de publication initiale du commentaire',
                "type": "date",
            },
            'updatedAt': {
                'name': 'Date de dernière modification',
                'description': 'Date de la dernière édition du commentaire, si applicable',
                "type": "date",
            },
            'likeCount': {
                'name': 'Nombre de likes',
                'description': 'Nombre de likes que le commentaire a reçu (au moment de la dernière mise à jour)',
                "type": "integer",
            },
            '_deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle le commentaire a été supprimé, si applicable',
                "type": "date",
            },
            'numberOfReplies': {
                'name': 'Nombre de réponses',
                'description': 'Nombre de commentaires répondant au commentaire, si applicable',
                "type": "integer",
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
                "name": "update frequency",
                "type": "integer",
                "options": {"admin_only": True}
            },
        }

    basicFields = {
        '_ident': ['id'],
        'text': ['snippet', 'textDisplay'],
    }
    dateTimeFields = {
        'publishedAt': ['snippet', 'publishedAt'],
        'updatedAt': ['snippet', 'updatedAt'],
    }
    statistics = {
        'like_counts': ['snippet', 'likeCount'],
    }

    class Meta:
        app_label = "Youtube"

    def __str__(self):
        target = self.parent_comment or self.video_target or self.channel_target or "an unidentified target"
        author = self.author or "An unidentified user"
        type = 'reply' if self.parent_comment else 'comment'
        return "%s\'s %s on %s" % (author, type, target)

    def get_obj_ident(self):
        return "YTComment__%s" % self.pk

    def ident(self):
        return self._ident

    def getLink(self):
        if not self.author.title:
            return None
        return "/youtube/comment/%s" % self.pk

    def navigation_context(self):
        if self.parent_comment:
            navigator = self.parent_comment.navigation_context()
            navigator.append(("Réponse de %s" % self.author, self.getLink()))
        elif self.video_target:
            navigator = self.video_target.navigation_context()
            navigator.append(("Commentaire de %s" % self.author, self.getLink()))
        elif self.channel_target:
            navigator = self.channel_target.navigation_context()
            navigator.append(("Commentaire de %s" % self.author, self.getLink()))
        else:
            navigator = self.author.navigation_context()
            navigator.append(("Commentaire sur cible inconnue", self.getLink()))
        return navigator

    def update(self, jObject):
        assert isinstance(jObject, dict), 'jObject must be a dict or json instance!'
        # pretty(jObject)
        self.copyBasicFields(jObject)
        self.truncate_text()
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateAuthor(jObject)
        self.updateChannelTarget(jObject)
        self.updateParentComment(jObject)
        self.updateVideoTarget(jObject)
        self._last_updated = today()
        self.save()

    def truncate_text(self):
        if not self.text:
            self.text = ""
        if len(self.text) >= self._text_max_length:
            self.text = self.text[0: self._text_max_length - 3] + '...'
            log('%s\'s text has been truncated!' % self)

    # @youtubeLogger.debug()
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

    # @youtubeLogger.debug()
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

    # @youtubeLogger.debug()
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    log('Invalid dict sequence: %s' % self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(comment=self, value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(comment=self, value=val)

    def updateVideoTarget(self, jObject):
        if self.video_target: return
        if self.parent_comment: return
        if 'videoId' in jObject['snippet']:
            if self.channel_target:
                video, new = YTVideo.objects.get_or_create(_ident=jObject['snippet']['videoId'])
                if new:
                    video.channel = self.channel_target
                    video.save()
                    videoToUpdateQueue.put(video)
            elif YTVideo.objects.filter(_ident=jObject['snippet']['videoId']).exists():
                video = YTVideo.objects.get(_ident=jObject['snippet']['videoId'])
                self.channel_target = video.channel
            else:
                return
            self.video_target = video

    def updateChannelTarget(self, jObject):
        if 'channelId' in jObject['snippet']:
            channel = YTChannel.objects.get(_ident=jObject['snippet']['channelId'])
            self.channel_target = channel

    def updateAuthor(self, jObject):
        if self.author: return
        if 'authorChannelId' in jObject['snippet'] and jObject['snippet']['authorChannelId']['value'] != '':
            channel, new = YTChannel.objects.get_or_create(_ident=jObject['snippet']['authorChannelId']['value'])
            if new:
                channelUpdateQueue.put(channel)
                channelToSubsHarvestQueue.put(channel)
            self.author = channel

    def updateParentComment(self, jObject):
        if self.parent_comment: return
        if 'parentId' in jObject['snippet']:
            comment, new = YTComment.objects.get_or_create(_ident=jObject['snippet']['parentId'])
            if new:
                commentToUpdateQueue.put(comment)
            self.parent_comment = comment


# OBJECT SAMPLE. MORE AT https://developers.google.com/youtube/v3/docs/comments
'''
{
    "kind": "youtube#comment",
    "etag": etag,
    "id": string,
    "snippet": {
        "authorDisplayName": string,
        "authorProfileImageUrl": string,
        "authorChannelUrl": string,
        "authorChannelId": {
            "value": string
        },
        "channelId": string,
        "videoId": string,
        "textDisplay": string,
        "textOriginal": string,
        "parentId": string,
        "canRate": boolean,
        "viewerRating": string,
        "likeCount": unsigned integer,
        "moderationStatus": string,
        "publishedAt": datetime,
        "updatedAt": datetime
    }
}
'''


class LikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='like_counts', null=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(YTComment, related_name='like_counts', null=True, on_delete=models.CASCADE)
