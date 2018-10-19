####################### YTCHANNEL  #######################
from django.db import models

from SocialNetworkHarvester.models import (
    Big_integer_time_label,
    Integer_time_label,
    Image_time_label,
    time_label
)
from .YTChannel import YTChannel
from .YTComment import YTComment
from .YTVideo import YTVideo


class SubscriberCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriber_counts', on_delete=models.CASCADE)


class VideoCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='video_counts', on_delete=models.CASCADE)


class Subscription(time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriptions', on_delete=models.CASCADE)
    value = models.ForeignKey(YTChannel, related_name='subscribers', on_delete=models.CASCADE)
    ended = models.DateTimeField(null=True)


#######################  YTVIDEO  ########################

class CommentCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='comment_counts', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='comment_counts', null=True, on_delete=models.CASCADE)


class ViewCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='view_counts', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='view_counts', null=True, on_delete=models.CASCADE)


class DislikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='dislike_counts', null=True, on_delete=models.CASCADE)


class FavoriteCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='favorite_counts', null=True, on_delete=models.CASCADE)


class ContentImage(Image_time_label):
    channel = models.ForeignKey(YTChannel, related_name='images', null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='images', null=True, on_delete=models.CASCADE)


#######################  YTCOMMENT  ######################

class LikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='like_counts', null=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(YTComment, related_name='like_counts', null=True, on_delete=models.CASCADE)
