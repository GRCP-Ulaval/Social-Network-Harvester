import queue
import threading

from SocialNetworkHarvester.loggers.jobsLogger import log


class TaskIndexer:
    _totals_tasks_distributed = {}

    def __init__(self):
        self._tasks_queues = {}
        self._mutex = threading.Lock()

    def total_size(self):
        with self._mutex:
            total = 0
            for task_queue in self._tasks_queues.values():
                total += task_queue.qsize()
            return total

    def count(self, task):
        task_queue = self._get_queue(task.__name__)
        return task_queue.qsize()

    def empty(self):
        return self.total_size() == 0

    def _get_next_queue_by_priority(self):
        with self._mutex:
            resulting_q = None
            for q in self._tasks_queues.values():
                if not resulting_q or q.qsize() > resulting_q.qsize():
                    resulting_q = q
            return resulting_q

    def get(self):
        resulting_q = self._get_next_queue_by_priority()
        if resulting_q:
            result = resulting_q.get()
            self._increment_total_tasks_distributed(result[0].__name__)
            return result
        return None, None, None

    def _increment_total_tasks_distributed(self, name):
        if name not in self._totals_tasks_distributed:
            self._totals_tasks_distributed[name] = 0
        self._totals_tasks_distributed[name] += 1

    def get_total_task_distributed(self, name):
        if name not in self._totals_tasks_distributed:
            self._totals_tasks_distributed[name] = 0
        return self._totals_tasks_distributed[name]

    def add(self, task, args=[], kwargs={}):
        task_queue = self._get_queue(task.__name__)
        task_queue.put((task, args, kwargs))

    def _get_queue(self, task_name):
        with self._mutex:
            if task_name not in self._tasks_queues:
                self._tasks_queues[task_name] = queue.Queue()
            return self._tasks_queues[task_name]

    def formated_tasks_counts(self):
        with self._mutex:
            formated_string = 'Current tasks to execute: {\n'
            for name, q in self._tasks_queues.items():
                formated_string += '{:>30}: {} (total: {})\n'.format(
                    name, q.qsize(), self.get_total_task_distributed(name)
                )
            formated_string += '}'
            return formated_string

    def clear(self):
        with self._mutex:
            for q in self._tasks_queues.values():
                del q
        log("Cleared the tasks queues.")
