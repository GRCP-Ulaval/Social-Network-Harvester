from django.db import models

from SocialNetworkHarvester.models import GenericModel, djangoNow
from .FBComment import FBComment
from .FBPost import FBPost
from .FBProfile import FBProfile


class FBReaction(GenericModel):
    from_profile = models.ForeignKey(
        FBProfile,
        related_name="posted_reactions",
        on_delete=models.PROTECT
    )
    to_post = models.ForeignKey(
        FBPost,
        related_name="received_reactions",
        null=True,
        on_delete=models.PROTECT
    )
    to_comment = models.ForeignKey(
        FBComment,
        related_name="received_reactions",
        null=True,
        on_delete=models.PROTECT
    )
    type = models.CharField(
        max_length=10,
        default="LIKE"
    )
    from_time = models.DateTimeField(
        default=djangoNow
    )
    until_time = models.DateTimeField(
        null=True
    )

    def get_fields_description(self):
        return {
            "from_profile": {
                "name": "from_profile",
                "description": ""
            },
            "to_post": {
                "name": "to_post",
                "description": ""
            },
            "to_comment": {
                "name": "to_comment",
                "description": ""
            },
            "type": {
                "name": "type",
                "description": ""
            },
            "from_time": {
                "name": "from_time",
                "description": ""
            },
            "until_time": {
                "name": "until_time",
                "description": ""
            },
        }
