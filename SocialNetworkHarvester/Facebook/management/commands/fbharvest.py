import datetime

from django.core.management.base import BaseCommand
from tendo import singleton

from SocialNetworkHarvester.loggers.facebookLogger import log, logError, facebookLogger
from SocialNetworkHarvester.settings import DEBUG
from .harvest.harvest import harvestFacebook, myEmailTitle, myEmailMessage, send_routine_email

now = datetime.datetime.now()
facebookLogger.reset_log()

class Command(BaseCommand):
    help = 'Search the Facebook\'s API for new content'

    def handle(self, *args, **options):
        me = singleton.SingleInstance(flavor_id="cronfb")
        m = '%s: Will run the Facebook harvester' % now.strftime('%y-%m-%d %H:%M')
        print(m)
        log(m)
        try:
            harvestFacebook()
        except:
            myEmailMessage[0] = 'FACEBOOK HARVEST ROUTINE HAS ENCOUNTERED A TOP-LEVEL ERROR:'
            logError(myEmailMessage[0])
        finally:
            print(myEmailTitle[0])
            print(myEmailMessage[0])
            log("The harvest has ended for the Facebook harvesters", showTime=True)
            if not DEBUG:
                send_routine_email(myEmailTitle[0], myEmailMessage[0])
