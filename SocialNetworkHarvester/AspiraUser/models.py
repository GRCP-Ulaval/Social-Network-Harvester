import pickle
import random
import re

import facebook
from django.contrib.auth.models import User

from Collection.models import Collection, CollectionItem
from Facebook.models import FBPage, FBPost, FBComment, FBReaction, FBUser
from SocialNetworkHarvester.loggers.viewsLogger import logError
from SocialNetworkHarvester.settings import FACEBOOK_APP_PARAMS
from Twitter.models import *
from Youtube.models import YTChannel, YTPlaylist, Subscription, YTVideo, YTComment, YTPlaylistItem


class UserProfile(models.Model):
    class Meta:
        app_label = "AspiraUser"

    def __str__(self):
        return "%s's user profile" % self.user

    user = models.OneToOneField(User, related_name="userProfile", null=False, on_delete=models.CASCADE)

    twitterApp_consumerKey = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_consumer_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_key = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_parameters_error = models.BooleanField(default=False)
    twitterUsersToHarvest = models.ManyToManyField(TWUser, related_name="harvested_by", blank=True)
    twitterUsersToHarvestLimit = models.IntegerField(default=30, blank=True)
    twitterHashtagsToHarvest = models.ManyToManyField(HashtagHarvester, related_name="harvested_by", blank=True)
    twitterHashtagsToHarvestLimit = models.IntegerField(default=5, blank=True)

    facebookApp_parameters_error = models.BooleanField(default=False)
    facebookPagesToHarvest = models.ManyToManyField(FBPage, related_name="harvested_by", blank=True)
    facebookPagesToHarvestLimit = models.IntegerField(default=20, blank=True)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)
    youtubeApp_parameters_error = models.BooleanField(default=False)
    ytChannelsToHarvest = models.ManyToManyField(YTChannel, related_name="harvested_by", blank=True)
    ytChannelsToHarvestLimit = models.IntegerField(default=100, blank=True)
    ytPlaylistsToHarvest = models.ManyToManyField(YTPlaylist, related_name="harvested_by", blank=True)
    ytPlaylistsToHarvestLimit = models.IntegerField(default=5, blank=True)

    passwordResetToken = models.CharField(max_length=255, null=True, blank=True, unique=True)
    passwordResetDateLimit = models.DateTimeField(null=True)

    def twitter_app_valid(self):
        return not self.twitterApp_parameters_error

    def facebook_app_valid(self):
        return not self.facebookApp_parameters_error

    def youtube_app_valid(self):
        return not self.youtubeApp_parameters_error

    @staticmethod
    def getUniquePasswordResetToken():
        token = getRandomString(length=254)
        while UserProfile.objects.filter(passwordResetToken=token).exists():
            token = getRandomString()
        return token

    @staticmethod
    def getHarvestables():
        return {
            'TWUser': 'twitterUsersToHarvest',
            'HashtagHarvester': 'twitterHashtagsToHarvest',
            'FBPage': 'facebookPagesToHarvest',
            'YTChannel': 'ytChannelsToHarvest',
            'YTPlaylist': 'ytPlaylistsToHarvest',
        }

    def getHarvested(self, modelName, kwargs={}):
        if modelName not in self.harvestableModels(): raise Exception("Wrong model name specified")
        if kwargs:
            return getattr(self, self.harvestableModels()[modelName]).filter(**kwargs)
        return getattr(self, self.harvestableModels()[modelName]).all()


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


class TableRowsSelection(models.Model):
    class Meta:
        app_label = "AspiraUser"

    user = models.ForeignKey(User, related_name="tableRowsSelections", on_delete=models.CASCADE)
    pageUrl = models.CharField(max_length=100)

    def __str__(self):
        return "%s's selection on %s" % (self.user, self.pageUrl)

    # @viewsLogger.debug(showArgs=True)
    def selectRow(self, table_id, queryset):
        oldQueryset = self.getSavedQueryset(queryset.model._meta.object_name, table_id)
        newQueryset = oldQueryset | queryset
        self.saveQuerySet(newQueryset, table_id)

    # @viewsLogger.debug(showArgs=True)
    def unselectRow(self, table_id, queryset):
        oldQueryset = self.getSavedQueryset(queryset.model._meta.object_name, table_id)
        newQueryset = oldQueryset.exclude(pk__in=queryset)
        self.saveQuerySet(newQueryset, table_id)

    # @viewsLogger.debug(showArgs=True)
    def saveQuerySet(self, queryset, table_id):
        selectQuery = self.queries.filter(table_id=table_id)
        if not selectQuery.exists():
            selectQuery = selectionQuery.objects.create(
                selection_group=self,
                query=pickle.dumps(queryset.query),
                model=queryset.model._meta.object_name,
                table_id=table_id)
        else:
            selectQuery = selectQuery[0]
            selectQuery.setQueryset(queryset)

    # @viewsLogger.debug(showArgs=True)
    def getSavedQueryset(self, modelName, table_id):
        selectQuery = self.queries.filter(table_id=table_id)
        if not selectQuery.exists():
            if not modelName: raise Exception('Must have a modelName argument to create a new query!')
            newQueryset = getModel(modelName).objects.none()
            selectQuery = selectionQuery.objects.create(
                selection_group=self,
                query=pickle.dumps(newQueryset.query),
                model=modelName,
                table_id=table_id)
        else:
            selectQuery = selectQuery[0]
        return selectQuery.getQueryset()

    def getSelectedRowCount(self):
        counts = {}
        for query in self.queries.all():
            counts[query.table_id] = query.getQueryset().distinct().count()
        return counts

    # @viewsLogger.debug(showArgs=True)
    def getQueryOptions(self, tableId):
        query = self.queries.filter(table_id=tableId)
        cleanOptions = {}
        if query.exists():
            options = query[0].miscOptions
            for option in options.split(';'):
                if option != '':
                    key, value = option.split('=')
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                    cleanOptions[key] = value
        return cleanOptions

    # @viewsLogger.debug(showArgs=True)
    def setQueryOption(self, tableId, optionName, optionValue):
        query = self.queries.filter(table_id=tableId)
        if query.exists():
            if not optionValue:
                query[0].removeOption(optionName)
            else:
                query[0].addOption(optionName, optionValue)


class selectionQuery(models.Model):
    """Stores a queryset's model name and query commandinstead of the whole queryset.
    """
    selection_group = models.ForeignKey(TableRowsSelection, related_name="queries", on_delete=models.CASCADE)
    query = models.BinaryField(max_length=1000)
    model = models.CharField(max_length=25)
    table_id = models.CharField(null=False, max_length=50)
    miscOptions = models.CharField(max_length=1000, default="")

    def __str__(self):
        return '%s\'s selectionQuery' % self.model

    # @viewsLogger.debug(showArgs=True)
    def getQueryset(self):
        query = pickle.loads(self.query)
        queryset = getModel(self.model).objects.none()
        queryset.query = query
        return queryset

    # @viewsLogger.debug(showArgs=True)
    def setQueryset(self, queryset):
        self.query = pickle.dumps(queryset.all().query)
        self.save()

    def addOption(self, optionName, optionValue=True):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;" % optionName, "", currentOptions)
        currentOptions += "%s=%s;" % (optionName, optionValue)
        self.miscOptions = currentOptions
        self.save()

    def removeOption(self, optionName):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;" % optionName, "", currentOptions)
        self.miscOptions = currentOptions
        self.save()

    def getOptionValue(self, optionName):
        currentOptions = self.miscOptions
        if not optionName in currentOptions:
            return None
        return re.match(r'%s=(?:[^;]+);' % optionName, currentOptions)


# @viewsLogger.debug(showArgs=True)
def getUserSelection(request):
    user = request.user
    pageURL = request.path
    if 'pageURL' in request.GET:
        pageURL = request.GET['pageURL']
    selection = TableRowsSelection.objects.filter(user=user, pageUrl=pageURL)
    if not selection.exists():
        selection = TableRowsSelection.objects.create(user=user, pageUrl=pageURL)
    return user.tableRowsSelections.filter(pageUrl=pageURL).first()


# @viewsLogger.debug(showArgs=False)
def resetUserSelection(request):
    user = request.user
    pageURL = request.path
    if 'pageURL' in request.GET:
        pageURL = request.GET['pageURL']
    selection = TableRowsSelection.objects.filter(user=user, pageUrl=pageURL)
    if selection.exists():
        selection[0].delete()
        TableRowsSelection.objects.create(user=user, pageUrl=pageURL)


def getRandomString(length=255):
    if length < 0: length = 255
    s = '%s%s%s' % (random.randint(0, 99999),
                    ''.join(random.choice(
                        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for i in
                            range(length)), int(time.time()))
    return "".join(random.sample(s, length))


MODEL_WHITELIST = ['FBPage', 'FBPost', 'FBComment', 'FBReaction', 'FBUser',
                   'Tweet', 'TWUser', "HashtagHarvester", "Hashtag", "favorite_tweet", "follower",
                   'YTChannel', 'YTVideo', 'YTPlaylist', 'Subscription', 'YTComment', 'YTPlaylistItem',
                   'Collection', 'CollectionItem'
                   ]


def getModel(modelName):
    if modelName not in MODEL_WHITELIST:
        raise Exception('Invalid or forbidden model name: %s' % modelName)
    return {model.__name__: model for model in [
        TWUser, Tweet, HashtagHarvester, follower, favorite_tweet, Hashtag,
        FBPage, FBPost, FBComment, FBReaction, FBUser,
        YTChannel, YTVideo, YTPlaylist, Subscription, YTComment, YTPlaylistItem,
        Collection, CollectionItem
    ]}[modelName]
