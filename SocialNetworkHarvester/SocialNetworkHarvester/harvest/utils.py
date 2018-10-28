import time
from queue import Empty

from SocialNetworkHarvester.harvest.globals import start_time, global_thread_stop_flag, job_counts_in_queue, \
    job_counts_in_queue_lock, tasks_queue
from SocialNetworkHarvester.utils import x_days_ago


def order_queryset(queryset, field_name, delay=1):
    is_null = field_name + "__isnull"
    lt = field_name + "__lt"
    ordered_elements = \
        queryset.filter(**{is_null: True}) | \
        queryset.filter(**{lt: x_days_ago(delay)}).order_by(field_name)
    return ordered_elements


def elapsed_seconds():
    return int(time.time() - start_time)


def safe_sleep(duration_in_seconds):
    init_time = time.time()
    while time.time() < init_time + duration_in_seconds:
        check_stop_flag_raised()
        time.sleep(0.5)


def check_stop_flag_raised():
    if global_thread_stop_flag[0]:
        raise GlobalStopFlagRaised


def increment_job_count(job_name):
    job_counts_in_queue_lock.acquire()
    if job_name in job_counts_in_queue[0]:
        job_counts_in_queue[0][job_name] += 1
    else:
        job_counts_in_queue[0][job_name] = 1
    job_counts_in_queue_lock.release()


def decrement_job_count(job_name):
    job_counts_in_queue_lock.acquire()
    if job_name not in job_counts_in_queue[0]:
        job_counts_in_queue_lock.release()
        raise Exception('Job %s is not registered in job_counts_in_queue' % job_name)
    else:
        job_counts_in_queue[0][job_name] -= 1
    job_counts_in_queue_lock.release()


def get_formated_job_counts():
    formated_string = 'Current tasks in queue: {\n'
    job_counts_in_queue_lock.acquire()
    for key, val in job_counts_in_queue[0].items():
        formated_string += f'{key:>40}: {val}\n'
    job_counts_in_queue_lock.release()
    formated_string += '}'
    return formated_string


def add_task(task, args=[], kwargs={}):
    tasks_queue.put((task, args, kwargs))
    increment_job_count(task.__name__)


def get_task():
    try:
        task, args, kwargs = tasks_queue.get(timeout=1)
    except Empty:
        return None, None, None
    decrement_job_count(task.__name__)
    return task, args, kwargs


def get_running_time_in_seconds():
    return time.time() - start_time


def get_running_time_in_minutes():
    return get_running_time_in_seconds() / 60


class NonFatalExeption(Exception):
    pass


class GlobalStopFlagRaised(Exception):
    pass


class MailReportableException(Exception):
    def __init__(self, title, message):
        self.title = title
        self.message = message
        super().__init__("An Error has to be reported by mail: %s" % title)


class MailReportableNonFatalException(MailReportableException, NonFatalExeption):
    pass
