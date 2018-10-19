from django.db import models

from SocialNetworkHarvester.loggers.viewsLogger import log
from SocialNetworkHarvester.models import replaceEmojisFromFields
from SocialNetworkHarvester.utils import today
from .FBProfile import FBProfile


class FBPost(models.Model):
    _ident = models.CharField(max_length=255, unique=True)
    admin_creator = models.CharField(max_length=128, null=True)
    caption = models.CharField(max_length=1024, null=True)
    created_time = models.DateTimeField(null=True)
    deleted_time = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    from_profile = models.ForeignKey(FBProfile, related_name="postedStatuses", null=True, on_delete=models.PROTECT)
    to_profiles = models.ManyToManyField(FBProfile, related_name="targetedByStatuses")
    is_hidden = models.BooleanField(default=False)
    is_instagram_eligible = models.BooleanField(default=False)
    link = models.CharField(max_length=4096, null=True)
    message = models.TextField(null=True)
    message_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostMessages")
    story = models.CharField(max_length=512, null=True)
    # story_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostStories")
    name = models.CharField(max_length=256, null=True)
    object_id = models.CharField(max_length=128, null=True)
    parent_post = models.ForeignKey("self", related_name="child_posts", null=True, on_delete=models.PROTECT)
    permalink_url = models.CharField(max_length=256, null=True)
    picture = models.CharField(max_length=2048, null=True)
    source = models.CharField(max_length=1024, null=True)
    status_type = models.CharField(max_length=64, null=True, )
    type = models.CharField(max_length=64, null=True, )
    updated_time = models.DateTimeField(null=True)

    ### Statistics fields ###
    share_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    comment_count = models.IntegerField(null=True)

    ### Management fields ###
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)
    last_comments_harvested = models.DateTimeField(null=True)
    last_reaction_harvested = models.DateTimeField(null=True)

    def __str__(self):
        from_profile = self.from_profile
        if from_profile:
            return "Status de %s" % from_profile.getInstance()
        else:
            return "Status à autheur non-identifié"

    def getStr(self):
        return str(self)

    def getTypeFrench(self):
        d = {
            'link': 'Lien',
            'status': 'Status',
            'photo': 'Photo',
            'video': 'Vidéo',
            'offer': 'Offre commerciale',
        }
        if not self.type: return "Status de type indéfini"
        if self.type not in d: return self.type
        return d[self.type]

    def getLink(self):
        return "/facebook/post/%s" % self.pk

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "String unique identifiant le status",
                "type": "integer"
            },
            "admin_creator": {
                "name": "Créateur-administrateur",
                "description": "Profil Facebook auteur du status (généralement le même que \"Auteur\"",
                "type": "object"
            },
            "caption": {
                "name": "Légende",
                "description": "Légende (sous-titre) du status.",
                "type": "long_string",
                "searchable": True,
            },
            "created_time": {
                "name": "Date de création",
                "description": "Date de création du status",
                "type": "date"
            },
            "description": {
                "name": "Description",
                "description": "Description du status",
                "type": "long_string",
                "searchable": True,
            },
            "from_profile": {
                "name": "Profil auteur",
                "description": "Profil Facebook auteur du status",
                "type": "object"
            },
            "to_profiles": {
                "name": "Profils visés",
                "description": "Profils Facebook visés par le status. (Apparaitra dans leur journal",
                "type": "object_list",
            },
            "is_hidden": {
                "name": "Caché",
                "description": "Détermine si le status est visible publiquement",
                "type": "boolean"
            },
            "is_instagram_eligible": {
                "name": "Éligible pour Instagram",
                "description": "Détermine si le status peut être partagé sur Instagram",
                "type": "boolean"
            },
            "link": {
                "name": "Lien",
                "description": "Lien contenu dans le status",
                "type": "link_url"
            },
            "message": {
                "name": "Message",
                "description": "Message attaché au status",
                "type": "long_string"
            },
            "message_tags": {
                "name": "Étiquettes de message",
                "description": "Étiquettes (tags) attachées au message",
                "type": "object_list",
            },
            "story": {
                "name": "Article",
                "description": "Titre de l'article attaché au status",
                "type": "long_string",
                "searchable": True,
            },
            "name": {
                "name": "Nom",
                "description": "Nom associé au status",
                "type": "short_string",
                "searchable": True,
            },
            "object_id": {
                "name": "Identifiant d'objet",
                "description": "String unique identifiant l'objet attaché sur Facebook (Photo,Video,etc)",
                "type": "integer"
            },
            "parent_post": {
                "name": "Status parent",
                "description": "Status mentionnant le profil auteur du présent status",
                "type": "object"
            },
            "permalink_url": {
                "name": "Lien permanent",
                "description": "URL Facebook permanent du status",
                "type": "link_url",
                "options": {
                    "displayable": False,
                    "downloadable": True
                }
            },
            "picture": {
                "name": "Image",
                "description": "Image incluse dans le status",
                "type": "image_url"
            },
            "source": {
                "name": "Source",
                "description": "Lien vers la vidéo ou l'application-flash mentionnée dans le status",
                "type": "link_url"
            },
            "type": {
                "name": "Type",
                "description": "Type de contenu du status. [link, status, photo, video, offer]",
                "type": "short_string"
            },
            "status_type": {
                "name": "Type de status",
                "description": "Type technique du status. [added_photos, created_event, tagged_in_photo, etc.]",
                "type": "long_string"
            },
            "updated_time": {
                "name": "Mis à jour",
                "description": "Date et heure de la dernière mise à jour du status sur Facebook",
                "type": "date"
            },
            "share_count": {
                "name": "Partages",
                "description": "Nombre de fois que le status as été partagé",
                "type": "integer"
            },
            "like_count": {
                "name": "Mentions j'aime",
                "description": "Nombre de personnes ayant aimé le status",
                "type": "integer"
            },
            "comment_count": {
                "name": "Commentaires",
                "description": "Nombre de commentaires en réaction au status",
                "type": "integer"
            },
            'last_updated': {
                'name': 'Last updated',
                'type': 'date',
                'options': {'admin_only': True},
            },
            'error_on_update': {
                'name': 'Error on update',
                'type': 'boolean',
                'options': {'admin_only': True},
            },
            'error_on_harvest': {
                'name': 'Error on harvest',
                'type': 'boolean',
                'options': {'admin_only': True},
            },
            'last_comments_harvested': {
                'name': 'Last cmts-harvested',
                'type': 'date',
                'options': {'admin_only': True},
            },
            'last_reaction_harvested': {
                'name': 'Last react-harvested',
                'type': 'date',
                'options': {'admin_only': True},
            },

        }

    def get_obj_ident(self):
        return "FBPost__%s" % self.pk

        ### UPDATE ROUTINE METHODS ###

    basicFields = {
        'caption': ['caption'],
        'created_time': ['created_time'],
        'description': ['description'],
        # 'from_profile':         ['from'],
        # 'to_profile':           ['to'],
        'is_hidden': ['is_hidden'],
        'is_instagram_eligible': ['is_instagram_eligible'],
        'link': ['link'],
        'message': ['message'],
        # 'message_tags':         ['message_tags'], #TODO: set all the connections
        'story': ['story'],
        # 'story_tags':           ['story_tags'], #TODO: set all the connections
        'name': ['name'],
        'object_id': ['object_id'],
        # 'parent_post':          ['parent_id'],
        'permalink_url': ['permalink_url'],
        'picture': ['picture'],
        'source': ['source'],
        'status_type': ['status_type'],
        'type': ['type'],
        'updated_time': ['updated_time'],
        'share_count': ['shares', 'count'],
        'like_count': ['likes', 'summary', 'total_count'],
        'comment_count': ['comments', 'summary', 'total_count'],
    }

    statistics = {
        'share_counts': ['shares', 'count'],
        'like_counts': ['likes', 'summary', 'total_count'],
        'comment_counts': ['comments', 'summary', 'total_count'],
    }

    # @facebookLogger.debug(showClass=True,showArgs=True)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object must be passed as argument.')

        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        replaceEmojisFromFields(self, ['message', 'description'])
        self.last_updated = today()
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
                    field = self._meta.get_field(attr)
                    if field.max_length and field.max_length < len(val) and field.max_length >= 30:
                        log("DATA TOO LONG TO FIT <%s> FIELD \"%s\" (value: %s)" % (self, attr, val))
                        val = "DATA TOO LONG. CONTENT SKIPPED"
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
                    # log('Invalid dict searching sequence: %s' % self.statistics[attrName])
                    val = None
                    break
            if val:
                if not countObjs.exists():
                    objType.objects.create(fbPost=self, value=val)
                else:
                    if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                        objType.objects.create(fbPost=self, value=val)
