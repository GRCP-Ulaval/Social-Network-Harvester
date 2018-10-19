from SocialNetworkHarvester.loggers.jobsLogger import log


def joinTWUsers(user1, user2):
    if user2.screen_name:
        user1.screen_name = user2.screen_name
    if user2._ident:
        user1._ident = user2._ident
    for label in [
        'screen_names',
        'names',
        'time_zones',
        'urls',
        'descriptions',
        'statuses_counts',
        'favourites_counts',
        'followers_counts',
        'friends_counts',
        'listed_counts',
    ]:
        log('transfering all %s from %s to %s' % (label, user2, user1))
        for item in getattr(user2, label).all():
            item.twuser = user1
            item.save()
    user1.save()
    user2.delete()
    return user1
