import os

from SocialNetworkHarvester.settings import LOG_DIRECTORY
from .base_logger import Logger

facebookLogger = Logger(
    loggerName='facebookLogger',
    filePath=os.path.join(LOG_DIRECTORY, "facebook.log"),
    append=False,
    indentation=2
)


def log(*args, **kwargs):
    facebookLogger.log(*args, **kwargs)


def pretty(*args, **kwargs):
    facebookLogger.pretty(*args, **kwargs)


def logError(*args, **kwargs):
    facebookLogger.exception(*args, **kwargs)
