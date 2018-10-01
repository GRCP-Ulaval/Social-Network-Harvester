from django.db import models

from SocialNetworkHarvester.loggers.viewsLogger import log


class FBAttachment(models.Model):
    description = models.TextField(null=True)
    imageUrl = models.CharField(max_length=1024, null=True)
    targetUrl = models.CharField(max_length=1024, null=True)
    title = models.CharField(max_length=512, null=True)
    type = models.CharField(max_length=32, null=True)

    def update(self, jObject):
        if 'description' in jObject:
            self.description = jObject['description']
        if 'media' in jObject and 'image' in jObject['media']:
            if 'url' in jObject['media']['image']:
                self.imageUrl = jObject['media']['image']['url']
            elif 'src' in jObject['media']['image']:
                self.imageUrl = jObject['media']['image']['src']
            else:
                log(jObject['media'])
        if 'target' in jObject:
            self.targetUrl = jObject['target']['url']
        if 'title' in jObject:
            self.title = jObject['title']
        if 'type' in jObject:
            self.type = jObject['type']
        self.save()
