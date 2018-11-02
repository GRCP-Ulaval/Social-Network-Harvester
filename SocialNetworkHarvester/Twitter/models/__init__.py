from .Hashtag import Hashtag
from .TWPlace import TWPlace
from .TWUser import TWUser, TWUrl
from .Tweet import Tweet
from .TwitterTimeLabels import (
    screen_name,
    name,
    time_zone,
    description,
    statuses_count,
    favourites_count,
    followers_count,
    friends_count,
    listed_count,
    follower,
    retweet_count,
    favorite_tweet,
)


def get_twitter_model_by_name(model_name):
    dict = {
        'screen_name': screen_name,
        'name': name,
        'time_zone': time_zone,
        'description': description,
        'statuses_count': statuses_count,
        'favourites_count': favourites_count,
        'followers_count': followers_count,
        'friends_count': friends_count,
        'listed_count': listed_count,
        'follower': follower,
        'retweet_count': retweet_count,
        'favorite_tweet': favorite_tweet,
        'url': TWUrl,
        'Hashtag': Hashtag,
        'TWPlace': TWPlace,
        'TWUser': TWUser,
        'Tweet': Tweet,
    }
    if model_name not in dict.keys():
        raise Exception('Invalid class name: {}'.format(model_name))
    return dict[model_name]
