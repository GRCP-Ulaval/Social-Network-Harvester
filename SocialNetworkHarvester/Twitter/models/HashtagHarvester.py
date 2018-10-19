from django.db import models

from .Hashtag import Hashtag


class HashtagHarvester(models.Model):
    class Meta:
        app_label = "Twitter"
        verbose_name = 'Hashtag Twitter'
        verbose_name_plural = 'Hashtags Twitter'

    hashtag = models.ForeignKey(Hashtag, related_name="harvesters", on_delete=models.CASCADE)
    _harvest_since = models.DateTimeField(null=True, blank=True)
    _harvest_until = models.DateTimeField(null=True, blank=True)
    _has_reached_begining = models.BooleanField(default=False)
    _last_harvested = models.DateTimeField(null=True, blank=True)

    def get_fields_description(self):
        return {
            "_harvest_since": {
                "name": "Collecte depuis",
                "description": "Date de début de la collecte (collecte les tweets émis après la date)",
                "type": "date",
                "options": {
                    "admin_only": False,
                }},
            "_harvest_until": {
                "name": "Collecte jusqu'à",
                "description": "Date de fin de la collecte (collecte les tweets émis avant la date)",
                "type": "date",
                "options": {
                    "admin_only": False,
                }},
            "_has_reached_begining": {
                'name': 'Collecte complétée',
                'description': 'Si la collecte est complétée pour la période spécifiée',
                "type": "boolean",
                "options": {
                    "admin_only": False,
                }},
            '_last_harvested': {
                'name': 'Dernière collecte',
                'description': 'Date de la dernière collecte pour ce hashtag',
                "type": "date",
                "options": {
                    "admin_only": False,
                }},
            'harvest_count': {
                'name': 'Nombre de résultats',
                'description': 'Nombre de tweets dans la base de données qui furent ajoutées suite à la recherche de '
                               'ce hashtag',
                "type": "integer"}
        }

    def __str__(self):
        since = "undefined"
        until = "undefined"
        if self._harvest_since:
            since = "%s-%s-%s" % (self._harvest_since.year, self._harvest_since.month, self._harvest_since.day)
        if self._harvest_until:
            until = "%s-%s-%s" % (self._harvest_until.year, self._harvest_until.month, self._harvest_until.day)
        return "#%s's harvester (%s to %s)" % (self.hashtag.term, since, until)

    def str(self):
        return str(self.hashtag)

    def harvest_count(self):
        return self.harvested_tweets.count()

    def get_obj_ident(self):
        return "HashtagHarvester__%s" % self.pk

    def getLink(self):
        return self.hashtag.getLink()
