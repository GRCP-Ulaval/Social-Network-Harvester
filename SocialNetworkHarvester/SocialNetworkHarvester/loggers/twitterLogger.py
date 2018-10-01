import os

from SocialNetworkHarvester.settings import DEBUG, LOG_DIRECTORY
from .base_logger import Logger

twitterLogger = Logger(
    loggerName='twitterLogger',
    filePath=os.path.join(LOG_DIRECTORY, "twitter.log"),
    append=False,
    indentation=2
)

def log(*args, **kwargs):
    twitterLogger.log(*args, **kwargs)


def pretty(*args, **kwargs):
    twitterLogger.pretty(*args, **kwargs)


def logError(*args, **kwargs):
    twitterLogger.exception(*args, **kwargs)
