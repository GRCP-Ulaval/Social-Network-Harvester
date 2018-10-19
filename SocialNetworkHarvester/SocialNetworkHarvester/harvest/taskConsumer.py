from SocialNetworkHarvester.harvest.baseThread import BaseThread
from SocialNetworkHarvester.harvest.globals import tasks_queue
from SocialNetworkHarvester.harvest.utils import check_stop_flag_raised
from SocialNetworkHarvester.loggers.jobsLogger import log


class TaskConsumer(BaseThread):
    relaunch_delay_in_seconds = 1
    name = None

    def __init__(self, name):
        self.name = name
        super().__init__()

    def execute(self):
        while tasks_queue.empty():
            check_stop_flag_raised()
        task, args, kwargs = tasks_queue.get()
        log('Consuming task: %s' % task.__name__)
        task(*args, **kwargs)
