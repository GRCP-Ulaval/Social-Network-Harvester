from datetime import datetime

from django.db import models
from django.utils.timezone import utc

from SocialNetworkHarvester.models import replaceEmojisFromFields


class FBVideo(models.Model):
    # TODO: Store more infos on videos (at least title?)
    _ident = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    updated_time = models.DateTimeField(null=True)

    def __str__(self):
        return "Vidéo Facebook"

    def getLink(self):
        return None

    def update(self, jObject):
        self._ident = jObject['id']
        if "description" in jObject:
            self.description = jObject['description']
        updated_time = datetime.strptime(jObject['updated_time'],
                                         '%Y-%m-%dT%H:%M:%S+0000')  # '2017-02-23T23:11:46+0000'
        replaceEmojisFromFields(self, ['description'])
        self.updated_time = updated_time.replace(tzinfo=utc)
        self.save()
