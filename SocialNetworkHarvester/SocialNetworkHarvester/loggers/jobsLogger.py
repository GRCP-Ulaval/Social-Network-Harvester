import os

from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from SocialNetworkHarvester.models import djangoNow
from SocialNetworkHarvester.settings import LOG_DIRECTORY, DEBUG
from .base_logger import Logger

jobsLogger = Logger(
    loggerName='jobsLogger',
    filePath=os.path.join(LOG_DIRECTORY, "harvest_job.log"),
    append=not DEBUG,
    indentation=2,
    showThread=True,
)


def log(*args, **kwargs):
    jobsLogger.log(*args, **kwargs)


def pretty(*args, **kwargs):
    jobsLogger.pretty(*args, **kwargs)


def logError(*args, **kwargs):
    jobsLogger.exception(*args, **kwargs)


def mail_log(title, message):
    logfilepath = os.path.join(LOG_DIRECTORY, 'harvest_job.log')
    logfile = open(logfilepath, 'r')
    adresses = [user.email for user in User.objects.filter(is_superuser=True)]
    try:
        email = EmailMessage(title, message)
        email.attachments = [('harvest_job.log', logfile.read(), 'text/plain')]
        email.to = adresses
        email.from_email = 'noreply.aspira.cron_routine_report'
        email.send()
        print('%s - Routine email sent to %s' % (djangoNow().strftime('%y-%m-%d_%H:%M'), adresses))
    except Exception as e:
        print('Routine email failed to send')
        print(e)
