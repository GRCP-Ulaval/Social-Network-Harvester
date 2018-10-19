from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from SocialNetworkHarvester.loggers.jobsLogger import log
from SocialNetworkHarvester.utils import today
from .YTChannel import YTChannel
from .YTVideo import YTVideo


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
        verbose_name = 'Commentaire Youtube'
        verbose_name_plural = 'Commentaires Youtube'

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
        self.updateChannelTarget(jObject)
        self.updateVideoTarget(jObject)
        self._last_updated = today()
        self.save()

    def truncate_text(self):
        if not self.text:
            self.text = ""
        if len(self.text) >= self._text_max_length:
            self.text = self.text[0: self._text_max_length - 3] + '...'
            log('%s\'s text has been truncated!' % self)

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
            self.author = channel
