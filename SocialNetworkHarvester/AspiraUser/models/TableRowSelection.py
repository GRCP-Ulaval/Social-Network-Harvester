import pickle
import re

from django.contrib.auth.models import User
from django.db import models

from AspiraUser.models import ItemHarvester
from Collection.models import Collection, CollectionItem
from Facebook.models import FBUser, FBReaction, FBComment, FBPost, FBPage
from Twitter.models import TWUser, Tweet, follower, favorite_tweet, Hashtag
from Youtube.models import YTChannel, YTVideo, YTPlaylist, Subscription, YTComment, YTPlaylistItem


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


MODEL_WHITELIST = ['FBPage', 'FBPost', 'FBComment', 'FBReaction', 'FBUser',
                   'Tweet', 'TWUser', "Hashtag", "favorite_tweet", "follower",
                   'YTChannel', 'YTVideo', 'YTPlaylist', 'Subscription', 'YTComment', 'YTPlaylistItem',
                   'Collection', 'CollectionItem', 'ItemHarvester'
                   ]


def getModel(modelName):
    if modelName not in MODEL_WHITELIST:
        raise Exception('Invalid or forbidden model name: %s' % modelName)
    return {model.__name__: model for model in [
        TWUser, Tweet, follower, favorite_tweet, Hashtag,
        FBPage, FBPost, FBComment, FBReaction, FBUser,
        YTChannel, YTVideo, YTPlaylist, Subscription, YTComment, YTPlaylistItem,
        Collection, CollectionItem,
        ItemHarvester
    ]}[modelName]
