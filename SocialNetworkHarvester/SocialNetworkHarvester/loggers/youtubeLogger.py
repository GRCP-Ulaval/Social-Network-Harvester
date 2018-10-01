import os

from SocialNetworkHarvester.settings import DEBUG, LOG_DIRECTORY
from .base_logger import Logger

youtubeLogger = Logger(
    loggerName='youtubeLogger',
    filePath=os.path.join(LOG_DIRECTORY, "youtube.log"),
    append=False,
    indentation=2
)

def log(*args, **kwargs):
    youtubeLogger.log(*args, **kwargs)


def pretty(*args, **kwargs):
    youtubeLogger.pretty(*args, **kwargs)


def logError(*args, **kwargs):
    youtubeLogger.exception(*args, **kwargs)
