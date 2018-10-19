from django.db import models


class Hashtag(models.Model):
    # TODO: be able to order hashtags by hit_count in an SQL query
    class Meta:
        app_label = "Twitter"
        verbose_name = 'Hashtag Twitter'
        verbose_name_plural = 'Hashtags Twitter'

    term = models.CharField(max_length=128, null=True)

    def get_fields_description(self):
        return {
            "term": {
                "name": "Terme",
                "description": "Mot ou terme du hastag. Sujet de la recherche",
                "type": "short_string",
                "searchable": True,
            },
            "hit_count": {
                "name": "Nombre de tweets",
                "description": "Nombre total de tweets dans la base de données contenant ce hashtag.",
                "type": "integer"
            }

        }

    def getLink(self):
        return "/twitter/hashtag/%s" % self.pk

    def __str__(self):
        return "#" + self.term

    def hit_count(self):
        return self.tweets.count()

    def get_obj_ident(self):
        return "Hashtag__%s" % self.pk
