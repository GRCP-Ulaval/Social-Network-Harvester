from SocialNetworkHarvester.harvest.globals import global_task_queue
from .baseThread import BaseThread
from .utils import safe_sleep, monitor_stop_flag


class BaseTaskProducer(BaseThread):
    task_injection_delay_in_seconds = 1
    in_between_routines_delay_in_seconds = 10
    task_queue_target_size = 1

    def __init__(self):
        super().__init__()
        requireds = ['generate_tasks']
        if not all([getattr(self, required) for required in requireds]):
            raise Exception(
                "The following attributes or methods must exist in %s: %s" % (self.__class__.__name__, requireds))

    def __str__(self):
        return self.name

    def execute(self):
        for task_group in self.generate_tasks():
            monitor_stop_flag()
            if task_group:
                global_task_queue.add(*task_group)
                safe_sleep(self.task_injection_delay_in_seconds)
                while global_task_queue.count(task_group[0]) >= self.task_queue_target_size:
                    safe_sleep(self.task_injection_delay_in_seconds)
        safe_sleep(self.in_between_routines_delay_in_seconds)

    def generate_tasks(self):
        """ This method should yield tuples of the following form:
            (<function 'target'>, <list 'args'>, <dict 'kwargs'>)
        """
        raise NotImplementedError()
