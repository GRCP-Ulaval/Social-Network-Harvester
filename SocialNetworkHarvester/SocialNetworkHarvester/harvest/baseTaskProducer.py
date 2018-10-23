from SocialNetworkHarvester.loggers.jobsLogger import log
from .baseThread import BaseThread
from .globals import tasks_queue
from .utils import safe_sleep, check_stop_flag_raised, add_task


class BaseTaskProducer(BaseThread):
    relaunch_delay_in_seconds = 60
    task_injection_delay_in_seconds = 0
    in_between_routines_delay_in_seconds = 30
    task_queue_max_size = 10

    def __init__(self):
        super().__init__()
        requireds = ['generate_tasks']
        if not all([getattr(self, required) for required in requireds]):
            raise Exception(
                "The following attributes or methods must exist in %s: %s" % (self.__class__.__name__, requireds))

    def execute(self):
        self.create_tasks()
        safe_sleep(self.in_between_routines_delay_in_seconds)

    def put_in_task_queue(self, task):
        while tasks_queue.qsize() > self.task_queue_max_size - 1:
            check_stop_flag_raised()
        add_task(*task)

    def create_tasks(self):
        for task in self.generate_tasks():
            check_stop_flag_raised()
            if task:
                self.put_in_task_queue(task)
                safe_sleep(self.task_injection_delay_in_seconds)

    def generate_tasks(self):
        """ This method should yield tuples of the following form:
            (<function 'target'>, <list 'args'>, <dict 'kwargs'>)
        """
        raise NotImplementedError()
