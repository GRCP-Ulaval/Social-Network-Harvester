import queue
import time
from datetime import datetime, timedelta

import psutil
from django.utils.timezone import utc

process = psutil.Process()

QUEUEMAXSIZE = 10000

threadsExitFlag = [False]


class CustomizedQueue(queue.Queue):
    def __init__(self, queueName):
        super().__init__(maxsize=QUEUEMAXSIZE)
        self._name = queueName


pageUpdateQueue = CustomizedQueue('pageUpdateQueue')  # stores FBPages
pageFeedHarvestQueue = CustomizedQueue('pageFeedHarvestQueue')  # stores FBPages
statusUpdateQueue = CustomizedQueue('statusUpdateQueue')  # stores FBPosts
commentUpdateQueue = CustomizedQueue('commentUpdateQueue')  # stores FBComments
profileUpdateQueue = CustomizedQueue('profileUpdateQueue')  # stores FBProfiles
reactionHarvestQueue = CustomizedQueue('reactionHarvestQueue')  # stores FBPosts and FBComments
commentHarvestQueue = CustomizedQueue('commentHarvestQueue')  # stores FBPosts

clientQueue = queue.Queue()  # stores client objects
exceptionQueue = queue.Queue()  # stores exceptions

allQueues = [pageUpdateQueue, pageFeedHarvestQueue, statusUpdateQueue, reactionHarvestQueue, commentHarvestQueue,
             commentUpdateQueue, profileUpdateQueue]


def today():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def xDaysAgo(x=0):
    return today() - timedelta(days=x)


startTime = time.time()


def elapsedSeconds():
    return int(time.time() - startTime)
