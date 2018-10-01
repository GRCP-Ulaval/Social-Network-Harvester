from SocialNetworkHarvester.models import *


class FBLocation(models.Model):
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    state = models.CharField(max_length=16, null=True)
    street = models.CharField(max_length=512, null=True)
    zip = models.CharField(max_length=255, null=True)

    def update(self, jObject):
        for attr in ['city', 'country', 'latitude', 'longitude', 'state', 'street', 'zip']:
            if attr in jObject:
                setattr(self, attr, jObject[attr])
        self.save()

    def __str__(self):
        str = ""
        if self.city:
            str += self.city + ', '
        if self.state:
            str += self.state + ", "
        if self.country:
            str += self.country
        return str
