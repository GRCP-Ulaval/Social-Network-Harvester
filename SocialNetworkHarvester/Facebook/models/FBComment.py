from django.db import models

from SocialNetworkHarvester.models import GenericModel, replaceEmojisFromFields, today
from .FBAttachment import FBAttachment
from .FBProfile import FBProfile
from .FBPost import FBPost


class FBComment(GenericModel):
    reference_name = 'fbComment'

    _ident = models.CharField(max_length=255, unique=True)
    from_profile = models.ForeignKey(FBProfile, related_name="posted_comments", null=True, on_delete=models.PROTECT)
    attachment = models.OneToOneField(FBAttachment, related_name="fbComments", null=True, on_delete=models.PROTECT)
    created_time = models.DateTimeField(null=True)
    deleted_time = models.DateTimeField(null=True)
    message = models.TextField(null=True)
    permalink_url = models.CharField(max_length=1024, null=True)
    parentPost = models.ForeignKey(FBPost, related_name="fbComments", null=True, on_delete=models.PROTECT)
    parentComment = models.ForeignKey("self", related_name="fbReplies", null=True, on_delete=models.PROTECT)

    ### Statistics fields ###
    comment_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)

    ### Management fields ###
    last_reaction_harvested = models.DateTimeField(null=True)
    last_comments_harvested = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)

    ### Utils ###

    def __str__(self):
        if self.parentPost:
            return "Commentaire de %s sur %s" % (self.from_profile, self.parentPost)
        elif self.parentComment:
            return "Réponse de %s à propos de %s" % (self.from_profile, self.parentComment)

    def getStr(self):
        return str(self)

    def getParent(self):
        if self.parentPost:
            return str(self.parentPost), "/facebook/post/%s" % self.parentPost.pk
        elif self.parentComment:
            return str(self.parentComment), "/facebook/comment/%s" % self.parentComment.pk

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "String unique identifiant le commentaire",
                "type": "short_string"
            },
            "from_profile": {
                "name": "Profil auteur",
                "description": "Profil Facebook auteur du commentaire",
                "type": "short_string"
            },
            "attachment": {
                "name": "Attaché",
                "description": "Élément attaché au commentaire",
                "type": "short_string"
            },
            "created_time": {
                "name": "Création",
                "description": "Date et heure de création du commentaire",
                "type": "date"
            },
            "deleted_time": {
                "name": "Délétion",
                "description": "Date de délétion du commentaire",
                "type": "date"
            },
            "message": {
                "name": "Message",
                "description": "Contenu du commentaire",
                "type": "long_string",
                "searchable": True
            },
            "permalink_url": {
                "name": "Lien permanent",
                "description": "Lien permanent vers le commentaire sur Facebook",
                "type": "link_url",
                "options": {
                    "displayable": False,
                    "downloadable": True,
                }
            },
            "parentPost": {
                "name": "Status parent",
                "description": "Status visé par le commentaire",
                "type": "object"
            },
            "parentComment": {
                "name": "Commentaire parent",
                "description": "Commentaire visé par le commentaire, s'il s'agit d'une réponse à un commentaire",
                "type": "long_string"
            },
            "comment_count": {
                "name": "Commentaires",
                "description": "Nombre de réponses posté au commentaire",
                "type": "integer"
            },
            "like_count": {
                "name": "Mentions j'aime",
                "description": "Nombre de mentions j'aime associées au commentaire",
                "type": "integer"
            },
        }

    ### Update routine ###
    basicFields = {
        "created_time": ['created_time'],
        "message": ['message'],
        "permalink_url": ['permalink_url'],
        "comment_count": ['comment_count'],
        "like_count": ['like_count'],
    }
    statistics = {
        "comment_counts": ['comment_count'],
        "like_counts": ['like_count'],
    }

    def update(self, jObject):
        super(FBComment, self).update(jObject)
        self.setAttachement(jObject)
        self.last_updated = today()
        replaceEmojisFromFields(self, ['message', ])
        self.save()

    def setAttachement(self, jObject):
        if "attachment" in jObject:
            if not self.attachment:
                self.attachment = FBAttachment.objects.create()
            self.attachment.update(jObject['attachment'])
