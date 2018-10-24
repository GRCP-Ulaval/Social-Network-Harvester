import re
import time
from datetime import datetime

from django.db import models

from SocialNetworkHarvester.loggers.jobsLogger import log
from SocialNetworkHarvester.utils import get_from_any_or_create, today
from .Hashtag import Hashtag
from .TWPlace import TWPlace
from .TWUser import TWUser


class Tweet(models.Model):
    class Meta:
        app_label = "Twitter"
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def __str__(self):
        return "%s tweet #%s" % (("@%s" % self.user if self.user else 'unidentifed TWUser'), self._ident)

    def get_obj_ident(self):
        return "Tweet__%s" % self.pk

    def get_ident(self):
        return self._ident

    _ident = models.BigIntegerField(unique=True)
    coordinates = models.CharField(max_length=255, null=True)
    contributors = models.ManyToManyField(TWUser, related_name="contributed_to")
    created_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    text = models.TextField(max_length=255, null=True)
    retweet_count = models.IntegerField(null=True)
    possibly_sensitive = models.BooleanField(default=False)
    place = models.ForeignKey(TWPlace, null=True, on_delete=models.PROTECT)
    source = models.CharField(max_length=255, null=True)
    lang = models.CharField(max_length=128)
    withheld_copyright = models.BooleanField(default=False)
    withheld_in_countries = models.CharField(max_length=255)
    withheld_scope = models.CharField(max_length=32)  # either “status” or “user”.
    user = models.ForeignKey(TWUser, related_name="tweets", null=True, on_delete=models.PROTECT)
    in_reply_to_user = models.ForeignKey(TWUser, null=True, related_name="replied_by", on_delete=models.PROTECT)
    in_reply_to_status = models.ForeignKey('self', null=True, related_name="replied_by", on_delete=models.PROTECT)
    quoted_status = models.ForeignKey('self', null=True, related_name="quoted_by", on_delete=models.PROTECT)
    retweet_of = models.ForeignKey('self', null=True, related_name="retweets", on_delete=models.PROTECT)
    user_mentions = models.ManyToManyField(TWUser, related_name="mentions")

    hashtags = models.ManyToManyField(Hashtag, related_name='tweets')

    _last_updated = models.DateTimeField(null=True)

    def last_updated(self):
        return self._last_updated

    _last_retweeter_harvested = models.DateTimeField(null=True)

    def last_retweeter_harvested(self):
        return self._last_retweeter_harvested

    _error_on_update = models.BooleanField(default=False)

    def error_on_update(self):
        return self._error_on_update

    _error_on_retweet_harvest = models.BooleanField(default=False)

    def error_on_retweet_harvest(self):
        return self._error_on_retweet_harvest

    _date_time_fields = ['created_at']
    _time_labels = ['retweet_count']
    _relationals = ['place_id', 'in_reply_to_user_id', 'in_reply_to_status_id', 'quoted_status_id', 'retweet_of_id',
                    'user_id', 'hashtags_id']

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "Nombre identificateur du tweet",
                "type": "short_string"},
            "coordinates": {
                "name": "Coordonnées",
                "description": "Coordonnées géographiques du tweet",
                "type": "short_string"},
            "contributors": {
                "name": "Contributeurs",
                "description": "Utilisateurs Twitter ayant contribué au tweet, en postant ou en éditant",
                "type": "object_list"},
            "created_at": {
                "name": "Création",
                "description": "Date et heure de publication du tweet",
                "type": "date"},
            "deleted_at": {
                "name": "Effacement",
                "description": "Date et heure d'effacement du tweet, si applicable",
                "type": "date"},
            "text": {
                "name": "Texte",
                "description": "Contenu textuel du tweet",
                "type": "long_string",
                "searchable": True,
            },
            "retweet_count": {
                "name": "Nombre de retweets",
                "description": "Dernière valeur enregistrée du nombre de retweets",
                "type": "integer"},
            "possibly_sensitive": {
                "name": "Possiblement sensible",
                "description": "(Booléen) Si le tweet pourrait être perçu comme offensant par un certain auditoire",
                "type": "boolean"},
            "place": {
                "name": "Place",
                "description": "Place(s) d'émission du tweet",
                "type": "short_string"},
            "source": {
                "name": "Source",
                "description": "Application utilisée pour publier le tweet",
                "type": "html_link"},
            "lang": {
                "name": "Language",
                "description": "Language du texte du tweet",
                "type": "short_string"},
            "withheld_copyright": {
                "name": "Droits d'auteurs",
                "description": "(Booléen) Si le tweet contient du matériel protégé par des droits d'auteurs",
                "type": "boolean"},
            "withheld_in_countries": {
                "name": "Retenu dans pays",
                "description": "Pays dans lesquels le tweet est masqué et n'apparait pas aux utilisateurs",
                "type": "short_string"},
            "withheld_scope": {
                "name": "Étendue de retenue",
                "description": "L'étendue de la politique de retenue si le tweet est masqué dans certains pays",
                "type": "short_string"},
            "user": {
                "name": "Auteur",
                "description": "Utilisateur Twitter ayant publié le tweet",
                "type": "object"},
            "in_reply_to_user": {
                "name": "En réponse à l'utilisateur",
                "description": "Utilisateur Twitter à qui le tweet répond, si applicable",
                "type": "object"},
            "in_reply_to_status": {
                "name": "En réponse au status",
                "description": "Tweet envers lequel le tweet répond, si applicable",
                "type": "object"},
            "quoted_status": {
                "name": "Status cité",
                "description": "Tweet cité dans le tweet. Différent d'un retweet.",
                "type": "object"},
            "retweet_of": {
                "name": "Retweet de",
                "description": "Tweet original du retweet, si applicable",
                "type": "object"},
            "userMentionsList": {
                "name": "Utilisateurs mentionnés",
                "description": "Utilisateurs Twitter mentionnés dans le texte",
                "type": "long_string",
                "options": {"displayable": False}},
            "hashtagsList": {
                "name": "Hashtags",
                "description": "Hashtags contenus dans le texte",
                "type": "long_string",
                "options": {"displayable": False}},
            "user_mentions": {
                "name": "Utilisateurs mentionnés",
                "description": "Utilisateurs Twitter mentionnés dans le texte",
                "type": "object_list",
                "options": {"downloadable": False}},
            "hashtags": {
                "name": "Hashtags",
                "description": "Hashtags contenus dans le texte",
                "type": "object_list",
                "options": {"downloadable": False}},
            "_last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {
                    "admin_only": True,
                }
            },
            "_last_retweeter_harvested": {
                "name": "Last retweet-harvested",
                "type": "date",
                "options": {
                    "admin_only": True,
                }
            },
            "_error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                }
            },
            "_error_on_retweet_harvest": {
                "name": "Error on retweet-harvest",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                }
            },
        }

    def getLink(self):
        return "/twitter/tweet/%s" % self.pk

    def _truncated_text(self, n):
        if self.text: return self.text[:n] + '...' * (len(self.text) > n)

    def truncated_text_25(self):
        return self._truncated_text(25)

    def truncated_text_50(self):
        return self._truncated_text(50)

    def truncated_text_100(self):
        return self._truncated_text(100)

    def hashtagsList(self):
        return ["#%s" % hashtag.term for hashtag in self.hashtags.all()]

    def userMentionsList(self):
        return ["@%s" % user.screen_name for user in self.user_mentions.all()]

    def digestSource(self):
        if self.source:
            return {
                "name": re.match(r"<a.*>(?P<name>.*)</a>", self.source).group("name"),
                "url": re.match(r'.*href="(?P<url>[^"]+)"', self.source).group("url")
            }

    # @twitterLogger.debug(showArgs=True)
    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateTimeLabels(jObject)
        if "entities" in jObject:
            self.setUserMentions(jObject['entities'])
            self.setHashtags(jObject['entities'])
        if "retweeted_status" in jObject:
            self.setRetweetOf(jObject['retweeted_status'])
        if 'user' in jObject and not self.user:
            self.setUser(jObject['user'])
        if jObject['in_reply_to_user_id']:
            self.setInReplyToUser(screen_name=jObject['in_reply_to_screen_name'], _ident=jObject['in_reply_to_user_id'])
            # self.setInReplyToUser(screen_name=jObject['in_reply_to_screen_name'], _ident=jObject[
            # 'in_reply_to_user_id'])
        if jObject['in_reply_to_status_id']:
            self.setInReplyToStatus(jObject['in_reply_to_status_id'])
        if 'quoted_status_id' in jObject:
            self.setQuotedStatus(jObject['quoted_status_id'])
        if jObject['place']:
            self.setPlace(jObject['place'])

        self._ident = jObject['id']
        try:
            self.save()
        except:
            text = self.text.encode('unicode-escape')
            # log('modified text: %s'%text)
            self.text = text
            self.save()

    def setUser(self, jObject):
        ident = jObject['id']
        screen_name = None
        if "screen_name" in jObject:
            screen_name = jObject['screen_name']
        try:
            twuser, new = get_from_any_or_create(TWUser, _ident=ident, screen_name=screen_name)
        except:
            doubles = TWUser.objects.filter(screen_name=screen_name)
            doubles[0]._has_duplicate = True
            doubles[0].save()
            log('TWUSER %s HAS %s DUPLICATES!' % (doubles[0], doubles.count() - 1))
            raise
            # twusers = TWUser.objects.filter(_ident=ident, screen_name=screen_name)
            # twuser = joinTWUsers(twusers[0], twusers[1])
        self.user = twuser

    def setInReplyToStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.in_reply_to_status = tweet

    def setInReplyToUser(self, **kwargs):
        try:
            twuser, new = get_from_any_or_create(TWUser, **kwargs)
        except:
            log('kwargs: %s' % kwargs)
            doubles = TWUser.objects.filter(**kwargs)
            doubles[0]._has_duplicate = True
            doubles[0].save()
            log('TWUSER %s HAS %s DUPLICATES!' % (doubles[0], doubles.count() - 1))
            time.sleep(3)
            raise
            # twusers = TWUser.objects.filter(**kwargs)
            # twuser = joinTWUsers(twusers[0], twusers[1])
        self.in_reply_to_user = twuser

    def setQuotedStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.quoted_status = tweet

    def setRetweetOf(self, jObject):
        tweet, new = Tweet.objects.get_or_create(_ident=jObject['id'])
        if new:
            tweet.UpdateFromResponse(jObject)
        self.retweet_of = tweet

    def setPlace(self, jObject):
        ident = jObject['id']
        place, new = TWPlace.objects.get_or_create(_ident=ident)
        if new:
            place.UpdateFromResponse(jObject)
        self.place = place

    def copyBasicFields(self, jObject):
        atrs = [x.attname for x in self._meta.fields if
                (x not in self._date_time_fields and
                 x.attname[0] != '_' and
                 x.attname not in self._relationals)]
        for atr in atrs:
            if atr in jObject and atr != 'id':
                setattr(self, atr, jObject[atr])

    def copyDateTimeFields(self, jObject):
        for atr in self._date_time_fields:
            if atr in jObject:
                dt = datetime.strptime(jObject[atr], '%a %b %d %H:%M:%S %z %Y')
                setattr(self, atr, dt)

    def updateTimeLabels(self, jObject):
        for atr in self._time_labels:
            if atr in jObject and jObject[atr]:
                related_name = atr + 's'
                lastItem = self.getLast(related_name)
                if not lastItem or lastItem.recorded_time != today():
                    className = globals()[atr]
                    newItem = className(tweet=self, value=jObject[atr])
                    newItem.save()
                elif lastItem.value != jObject[atr]:
                    lastItem.value = jObject[atr]
                    lastItem.save()

    def getLast(self, related_name):
        queryset = getattr(self, related_name).order_by('-recorded_time')
        if queryset.count() == 0:
            return None
        return queryset[0]

    # @twitterLogger.debug(showArgs=True)
    def setUserMentions(self, jObject):
        if "user_mentions" in jObject:
            for user_mention in jObject["user_mentions"]:
                twUser, new = get_from_any_or_create(TWUser, _ident=user_mention['id'])
                self.user_mentions.add(twUser)

    def setHashtags(self, jObject):
        if "hashtags" in jObject:
            for hashtag in jObject['hashtags']:
                hashtagObj, new = get_from_any_or_create(Hashtag, term=hashtag['text'])
                self.hashtags.add(hashtagObj)
