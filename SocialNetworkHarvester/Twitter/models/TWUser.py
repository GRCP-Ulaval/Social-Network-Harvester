import re
from datetime import datetime

from django.db import models

from SocialNetworkHarvester.models import Text_time_label
from SocialNetworkHarvester.utils import today


class TWUser(models.Model):
    screen_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    _ident = models.BigIntegerField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(null=True)
    geo_enabled = models.BooleanField(default=False)
    has_extended_profile = models.BooleanField(default=False)
    is_translation_enabled = models.BooleanField(default=False)
    is_translator = models.BooleanField(default=False)
    lang = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=255)
    profile_background_color = models.CharField(max_length=50)
    profile_background_image_url = models.CharField(max_length=500, null=True)
    profile_image_url = models.CharField(max_length=1024)
    protected = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    time_zone = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=500, null=True)
    statuses_count = models.IntegerField(null=True)
    favourites_count = models.IntegerField(null=True)
    followers_count = models.IntegerField(null=True)
    friends_count = models.IntegerField(null=True)
    listed_count = models.IntegerField(null=True)

    _date_time_fields = ['created_at']
    _time_labels = ['screen_name', 'name', 'time_zone', 'url', 'description',
                    'statuses_count', 'favourites_count', 'followers_count', 'friends_count', 'listed_count']

    _last_updated = models.DateTimeField(null=True)

    def last_updated(self):
        return self._last_updated

    _last_tweet_harvested = models.DateTimeField(null=True)

    def last_tweet_harvested(self):
        return self._last_tweet_harvested

    _last_friends_harvested = models.DateTimeField(null=True)

    def last_friends_harvested(self):
        return self._last_friends_harvested

    _last_followers_harvested = models.DateTimeField(null=True)

    def last_followers_harvested(self):
        return self._last_followers_harvested

    _last_fav_tweet_harvested = models.DateTimeField(null=True)

    def last_fav_tweet_harvested(self):
        return self._last_fav_tweet_harvested

    _error_on_update = models.BooleanField(default=False)

    def error_on_update(self):
        return self._error_on_update

    _has_duplicate = models.BooleanField(default=False)

    def has_duplicate(self):
        return self._has_duplicate

    _error_on_harvest = models.BooleanField(default=False)

    def error_on_harvest(self):
        return self._error_on_harvest

    _error_on_network_harvest = models.BooleanField(default=False)

    def error_on_network_harvest(self):
        return self._error_on_network_harvest

    _update_frequency = models.IntegerField(default=5)  # 1 = every day, 2 = every 2 days, etc.

    def update_frequency(self):
        return self._update_frequency

    _harvest_frequency = models.IntegerField(default=1)

    def harvest_frequency(self):
        return self._harvest_frequency

    _network_harvest_frequency = models.IntegerField(default=1)

    def network_harvest_frequency(self):
        return self._network_harvest_frequency

    _has_reached_begining = models.BooleanField(default=False)

    def has_reached_begining(self):
        return self._has_reached_begining

    @staticmethod
    def get_fields_description():
        return {
            "screen_name": {
                "description": "Nom d'utilisateur, identifiant le compte.",
                "name": "Nom d'utilisateur",
                "type": "short_string",
                "searchable": True,
            },
            "name": {
                "description": "Nom complet de l'utilisateur.",
                "name": "Nom",
                "type": "short_string",
                "searchable": True,
            },
            "_ident": {
                "description": "Numéro-identifiant du compte.",
                "name": "Identifiant",
                "type": "short_string"},
            "created_at": {
                "description": "Temps de création du compte.",
                "name": "Créé le",
                "type": "date"},
            "geo_enabled": {
                "description": "(Booléen) Si le compte a activé la géo-localisation.",
                "name": "Geo-Activé",
                "type": "boolean"},
            "has_extended_profile": {
                "description": "(Booléen) Si le compte a un profil étendu.",
                "name": "Profil Étendu",
                "type": "boolean"},
            "is_translator": {
                "description": "(Booléen) Si l'utilisateur du compte fait partie de la communauté des traducteurs "
                               "Twitter.",
                "name": "Est Traducteur",
                "type": "boolean"},
            "lang": {
                "description": "Langue première du compte.",
                "name": "Language",
                "type": "short_string"},
            "location": {
                "description": "Géo-location de l'utilisateur du compte. Peut ne pas être exact puisque les "
                               "utilisateurs choisissent ce qu'ils écrivent.",
                "name": "Location",
                "type": "short_string"},
            "protected": {
                "description": "(Booléen) Si le compte dénie la collecte de ses informations via l'API de Twitter",
                "name": "Protégé",
                "type": "boolean",
                "options": {
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }
            },
            "verified": {
                "description": "(Booléen) Si le compte as été vérifié comme légitime par un employé de Twitter.",
                "name": "Verifié",
                "type": "boolean",
                "options": {
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'red',
                            True: "green"
                        }
                    }
                }
            },
            "time_zone": {
                "description": "Fuseau horaire principal du compte.",
                "name": "Fuseau horaire",
                "type": "short_string"},
            "url": {
                "description": "Site web de l'utilisateur ou de l'organisation.",
                "name": "URL",
                "type": "link_url"},
            "description": {
                "description": "Description du compte, de l'utilisateur ou de l'organisation.",
                "name": "Description",
                "type": "long_string"},
            "statuses_count": {
                "description": "Nombre de status en date de la dernière collecte (généralement <24h).",
                "name": "Nombre de status",
                "type": "integer"},
            "favourites_count": {
                "description": "Nombre de tweets favoris en date de la dernière collecte (généralement <24h).",
                "name": "Nombre de favoris",
                "type": "integer"},
            "followers_count": {
                "description": "Nombre d'abonnés (followers) au compte en date de la dernière collecte (généralement "
                               "<24h).",
                "name": "Nombre d'abonnés",
                "type": "integer"},
            "friends_count": {
                "description": "Nombre de compte suivi par l'utilisateur en date de la dernière collecte.",
                "name": "Nombre d'abonnements",
                "type": "integer"},
            "listed_count": {
                "description": "nombre de listes publiques dans lesquelles le compte apparait.",
                "name": "Mentions publiques",
                "type": "integer"
            },
            "profile_image_url": {
                "description": "Url de l'image de profil de l'utilisateur (au moment de la dernière collecte).",
                "name": "Image de profil",
                "type": "image_url",
                "options": {
                    "render": lambda value: re.sub("_normal", "", value),
                }
            },
            "_last_updated": {
                "name": "Last updated",
                "type": "date",
                "options": {
                    "admin_only": True
                }},
            "_last_tweet_harvested": {
                "name": "Last tweet-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }},
            "_last_friends_harvested": {
                "name": "Last-friend-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }},
            "_last_followers_harvested": {
                "name": "Last followers-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }},
            "_last_fav_tweet_harvested": {
                "name": "Last fav-tweet-harvested",
                "type": "date",
                "options": {
                    "admin_only": True
                }},
            "_error_on_update": {
                "name": "Error on update",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_has_duplicate": {
                "name": "Has duplicate",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_error_on_harvest": {
                "name": "Error on harvest",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_error_on_network_harvest": {
                "name": "Error on network-harvest",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_update_frequency": {
                "name": "Update frequency",
                "type": "integer",
                "options": {
                    "admin_only": True
                }},
            "_harvest_frequency": {
                "name": "Harvest frequency",
                "type": "integer",
                "options": {
                    "admin_only": True,
                }},
            "_network_harvest_frequency": {
                "name": "Network-harvest frequency",
                "type": "integer",
                "options": {
                    "admin_only": True
                }},
            "_has_reached_begining": {
                "name": "Has reached begining",
                "type": "boolean",
                "options": {
                    "admin_only": True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'blue',
                            True: "green"
                        }
                    }
                }},
        }

    class Meta:
        app_label = "Twitter"
        verbose_name = 'Utilisateur Twitter'
        verbose_name_plural = 'Utilisateurs Twitter'

    def getLink(self):
        return "/twitter/user/%s" % self.pk

    def get_obj_ident(self):
        return "TWUser__%s" % self.pk

    def __str__(self):
        if self.screen_name:
            return self.screen_name
        else:
            return 'TWUser %s' % self._ident

    def __init__(self, *args, **kwargs):
        super(TWUser, self).__init__(*args, **kwargs)
        if 'jObject' in kwargs: self.UpdateFromResponse(kwargs['jObject'])

    def biggerImageUrl(self):
        return re.sub("_normal.", "_bigger.", self.profile_image_url)

    def UpdateFromResponse(self, response):
        # log('%s: %s' % (self, response))
        if not isinstance(response, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        # log('len(location): %s'%len(jObject['location']))
        # log('location: %s'%jObject['location'])
        self.copyBasicFields(response)
        self.copyDateTimeFields(response)
        self.updateTimeLabels(response)
        self._ident = response['id']
        self._last_updated = today()
        self.save()

    def getLast(self, related_name):
        queryset = getattr(self, related_name).order_by('-recorded_time')
        if queryset.count() == 0:
            return None
        return queryset[0]

    def copyBasicFields(self, jObject):
        for atr in [x.attname for x in self._meta.fields if x not in self._date_time_fields and x.attname[0] != '_']:
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
                    if atr == 'url':
                        # having a class named "url" breaks the Django import system.
                        className = TWUrl
                    else:
                        className = globals()[atr]
                    newItem = className(twuser=self, value=jObject[atr])
                    newItem.save()
                elif lastItem.value != jObject[atr]:
                    lastItem.value = jObject[atr]
                    lastItem.save()


class TWUrl(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="urls", on_delete=models.CASCADE)
