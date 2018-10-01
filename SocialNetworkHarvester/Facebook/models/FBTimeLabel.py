from django.db import models

from Facebook.models import FBPost, FBComment, FBPage
from SocialNetworkHarvester.models import Integer_time_label, Float_time_label


class like_count(Integer_time_label):
    fbPost = models.ForeignKey(
        FBPost,
        related_name="like_counts",
        null=True,
        on_delete=models.CASCADE
    )
    fbComment = models.ForeignKey(
        FBComment,
        related_name="like_counts",
        null=True,
        on_delete=models.CASCADE
    )


class comment_count(Integer_time_label):
    fbPost = models.ForeignKey(
        FBPost,
        related_name="comment_counts",
        null=True,
        on_delete=models.CASCADE
    )
    fbComment = models.ForeignKey(
        FBComment,
        related_name="comment_counts",
        null=True,
        on_delete=models.CASCADE
    )


class share_count(Integer_time_label):
    fbPost = models.ForeignKey(
        FBPost,
        related_name="share_counts",
        on_delete=models.CASCADE
    )


class checkins_count(Integer_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="checkins_counts",
        on_delete=models.CASCADE
    )


class fan_count(Integer_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="fan_counts",
        on_delete=models.CASCADE
    )


class overall_star_rating_count(Float_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="overall_star_rating_counts",
        on_delete=models.CASCADE
    )


class rating_count(Integer_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="rating_counts",
        on_delete=models.CASCADE
    )


class talking_about_count(Integer_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="talking_about_counts",
        on_delete=models.CASCADE
    )


class were_here_count(Integer_time_label):
    fbPage = models.ForeignKey(
        FBPage,
        related_name="were_here_counts",
        on_delete=models.CASCADE
    )
