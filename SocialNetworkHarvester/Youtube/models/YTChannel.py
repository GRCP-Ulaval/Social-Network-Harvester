from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from SocialNetworkHarvester.utils import today


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
        verbose_name = 'Chaîne Youtube'
        verbose_name_plural = 'Chaînes Youtube'

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
                    pass
                    # log('Invalid dict sequence: %s'%self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(channel=self, value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(channel=self, value=val)

    def updateImages(self, jObject):
        # TODO: Save a copy of the images on disk
        pass
