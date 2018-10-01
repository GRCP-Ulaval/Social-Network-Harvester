import os

from SocialNetworkHarvester.settings import DEBUG, LOG_DIRECTORY
from .base_logger import Logger

viewsLogger = Logger(
    loggerName='viewsLogger',
    filePath=os.path.join(LOG_DIRECTORY, "views.log"),
    append=False,
    indentation=2
)


def log(*args, **kwargs):
    viewsLogger.log(*args, **kwargs) if DEBUG else 0


def pretty(*args, **kwargs):
    viewsLogger.pretty(*args, **kwargs) if DEBUG else 0


def logError(*args, **kwargs):
    viewsLogger.exception(*args, **kwargs) if DEBUG else 0
