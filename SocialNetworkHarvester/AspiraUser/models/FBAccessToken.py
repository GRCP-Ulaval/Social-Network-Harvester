import time

import facebook
from django.db import models

from SocialNetworkHarvester.loggers.viewsLogger import pretty, log, logError
from SocialNetworkHarvester.settings import FACEBOOK_APP_PARAMS
from .UserProfile import UserProfile


class FBAccessToken(models.Model):
    class Meta:
        app_label = "Facebook"

    _token = models.CharField(max_length=255)
    expires = models.IntegerField(blank=True, null=True)
    # expires gives the "epoch date" of expiration of the token. Compare to time.time() to know if still valid.
    userProfile = models.OneToOneField(UserProfile, related_name="fbAccessToken", null=True, on_delete=models.CASCADE)

    def is_expired(self):
        if not self.expires: return True
        return time.time() >= self.expires

    def is_extended(self):
        return self.expires != None

    def __str__(self):
        return "%s's facebook access token" % self.userProfile.user

    def extend(self):
        try:
            graph = facebook.GraphAPI(self._token)
            response = graph.extend_access_token(FACEBOOK_APP_PARAMS['app_id'], FACEBOOK_APP_PARAMS['app_secret'])
            pretty(response)
            if not 'access_token' in response:
                raise Exception("failed to extend access token: %s" % self)
            self._token = response['access_token']
            if 'expires_in' in response:
                self.expires = time.time() + int(response['expires_in'])
            else:
                self.expires = time.time() + 60 * 5
            self.save()
            log("%s expires in %s seconds" % (self, self.expires - time.time()))
        except Exception as e:
            logError("An error occured while extending the token!")
            self.userProfile.facebookApp_parameters_error = True
            self.userProfile.save()
            raise
