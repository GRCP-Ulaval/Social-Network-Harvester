from threading import Thread

from SocialNetworkHarvester.loggers.jobsLogger import log, logError
from .globals import global_errors
from .utils import (
    NonFatalExeption,
    safe_sleep,
    monitor_stop_flag,
    GlobalStopFlag
)


class BaseThread(Thread):
    name = None
    relaunch_delay_in_seconds = 60

    def __init__(self):
        super().__init__()
        requireds = ['name']
        if not all([getattr(self, required) for required in requireds]):
            raise Exception(
                f"The following attributes or methods must "
                f"exist in {self.__class__.__name__}: {requireds}"
            )

    def run(self):
        log('%s has started' % self.name)
        try:
            while True:
                monitor_stop_flag()
                self.execute()
        except NonFatalExeption:
            logError(
                f"({self.name}) has encountered a non-fatal error. Relaunching "
                f"in {self.relaunch_delay_in_seconds} seconds"
            )
            safe_sleep(self.relaunch_delay_in_seconds)
            return self.run()
        except GlobalStopFlag:
            log("Thread ended gracefully.")
            return
        except Exception as e:
            global_errors.put((self, e))
            return

    def execute(self):
        raise NotImplementedError('BaseThread children must implement the execute() method.')

    def __str__(self):
        return self.name
