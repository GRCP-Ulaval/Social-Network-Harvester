from SocialNetworkHarvester.harvest.baseThread import BaseThread
from SocialNetworkHarvester.harvest.globals import global_task_queue
from SocialNetworkHarvester.harvest.utils import monitor_stop_flag


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
        while global_task_queue.empty():
            monitor_stop_flag()

        self.current_task, self.current_args, self.current_kwargs = global_task_queue.get()
        if not self.current_task:
            return
        # log('Consuming task: %s' % self.current_task.__name__)
        self.current_task(*self.current_args, **self.current_kwargs)
        self.current_task = self.current_args = self.current_kwargs = None

    def __str__(self):
        if self.current_task:
            return self.current_task.__name__
        return self.name
