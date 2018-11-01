import queue
import threading

from SocialNetworkHarvester.loggers.jobsLogger import log


class TaskIndexer:

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

    def _get_highest_queue_by_size(self):
        with self._mutex:
            resulting_q = None
            for q in self._tasks_queues.values():
                if not resulting_q:
                    resulting_q = q
                elif q.qsize() > resulting_q.qsize():
                    resulting_q = q
            return resulting_q

    def get(self):
        resulting_q = self._get_highest_queue_by_size()
        if resulting_q:
            return resulting_q.get()
        return None, None, None

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
                formated_string += f'{name:>40}: {q.qsize()}\n'
            formated_string += '}'
            return formated_string

    def clear(self):
        with self._mutex:
            self._tasks_queues = {}
        log("Cleared the tasks queues.")
