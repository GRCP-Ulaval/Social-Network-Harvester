from django.db import models


class FBUser(models.Model):
    _ident = models.CharField(max_length=225, unique=True)
    name = models.CharField(max_length=256, null=True)

    def get_obj_ident(self):
        return "FBUser__%s" % self.pk

    def get_fields_description(self):
        return {
            "_ident": {
                "description": "Identifiant numérique unique du profil",
                "name": "Identifiant",
                "type": "short_string"
            },
            "name": {
                "description": "Le nom affiché de la personne",
                "name": "Nom",
                "type": "short_string"
            },
        }

    def __str__(self):
        return self.name if self.name else "Utilisateur non-identifié"
