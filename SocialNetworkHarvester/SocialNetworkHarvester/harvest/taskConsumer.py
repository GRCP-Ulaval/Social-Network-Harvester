from SocialNetworkHarvester.harvest.baseThread import BaseThread
from SocialNetworkHarvester.harvest.globals import tasks_queue
from SocialNetworkHarvester.harvest.utils import check_stop_flag_raised, get_task
from SocialNetworkHarvester.loggers.jobsLogger import log


class TaskConsumer(BaseThread):
    relaunch_delay_in_seconds = 1
    name = None
    current_task = None
    current_args = None
    current_kwargs = None

    def __init__(self, name):
        self.name = name
        super().__init__()

    def execute(self):
        while tasks_queue.empty():
            check_stop_flag_raised()

        self.current_task, self.current_args, self.current_kwargs = get_task()
        if not self.current_task:
            return
        #log('Consuming task: %s' % self.current_task.__name__)
        self.current_task(*self.current_args, **self.current_kwargs)
        self.current_task = self.current_args = self.current_kwargs = None

    def __str__(self):
        if self.current_task:
            return f"{self.name} (current task: {self.current_task.__name__})"
        return f"{self.name} (current task: None)"
