from django.db import models


class TWPlace(models.Model):
    _ident = models.CharField(unique=True, max_length=255)
    attributes = models.CharField(max_length=500, null=True)
    bounding_box = models.CharField(max_length=500, null=True)
    country = models.CharField(max_length=128, null=True)
    full_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=128, null=True)
    place_type = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=255, null=True)

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifier",
                "description": "Identifier number of the Place object",
                "type": "short_string"},
            "attributes": {
                "name": "Attributes",
                "description": "(Composite) All values not explicitely stored in the Aspira's database",
                "type": "long_string"},
            "bounding_box": {
                "name": "Bounding box",
                "description": "Imaginary geographiqual square bounding the Place object",
                "type": "short_string"},
            "country": {
                "name": "Country",
                "description": "Coutry of the Place",
                "type": "short_string"},
            "full_name": {
                "name": "Full Name",
                "description": "Full arbitrary name of the Place",
                "type": "short_string"},
            "name": {
                "name": "Name",
                "description": "Short arbitrary name (or abbreviation) of the Place",
                "type": "short_string"},
            "place_type": {
                "name": "Place type",
                "description": "Type of the Place",
                "type": "short_string"},
            "url": {
                "name": "Url",
                "description": "Url associated with the Place object",
                "type": "link_url"}
        }

    class Meta:
        app_label = "Twitter"

    def __str__(self):
        if self.name:
            return self.name
        elif self.place_type and self._ident:
            return "%s #%s" % (self.place_type, self._ident)

    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        self.copyBasicFields(jObject)
        self._ident = jObject['id']
        self.save()

    def copyBasicFields(self, jObject):
        for atr in [x.attname for x in self._meta.fields if x.attname[0] != '_']:
            if atr in jObject and atr != 'id':
                setattr(self, atr, jObject[atr])

    def get_obj_ident(self):
        return "TWPlace__%s" % self.pk
