from threading import Thread

from SocialNetworkHarvester.loggers.jobsLogger import log, logError
from .globals import global_errors
from .utils import (
    NonFatalExeption,
    safe_sleep,
    check_stop_flag_raised,
    GlobalStopFlagRaised
)


class BaseThread(Thread):
    name = None
    relaunch_delay_in_seconds = 60

    def __init__(self):
        super().__init__()
        requireds = ['name']
        if not all([getattr(self, required) for required in requireds]):
            raise Exception(
                "The following attributes or methods must exist in %s: %s" % (self.__class__.__name__, requireds))

    def run(self):
        log('%s has started' % self.name)
        try:
            while True:
                check_stop_flag_raised()
                self.execute()
        except NonFatalExeption:
            logError("(%s) has encountered a non-fatal error. Relaunching in %s seconds" % (
                self.name, self.relaunch_delay_in_seconds
            ))
            safe_sleep(self.relaunch_delay_in_seconds)
            return self.run()
        except GlobalStopFlagRaised:
            log("Thread ended gracefully.")
            return
        except Exception as e:
            global_errors.put((self, e))
            return

    def execute(self):
        raise NotImplementedError('BaseThread children must implement the execute() method.')
