import time

from SocialNetworkHarvester.harvest.globals import start_time, global_thread_stop_flag, global_process
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
        monitor_stop_flag()
        time.sleep(0.5)


def monitor_stop_flag():
    if global_thread_stop_flag[0]:
        raise GlobalStopFlag


def get_running_time_in_seconds():
    return time.time() - start_time


def get_running_time_in_minutes():
    return get_running_time_in_seconds() / 60


def get_running_time_in_hours():
    return get_running_time_in_minutes() / 60


def get_formated_thread_list(thread_list):
    threads = {}
    for thread in thread_list:
        if hasattr(thread, 'current_task'):
            if hasattr(thread.current_task, '__name__'):
                threads[thread.name] = thread.current_task.__name__
            else:
                threads[thread.name] = 'idle'

    formated_string = 'Working threads: {\n'
    for thread_name, task_name in threads.items():
        formated_string += '{:>10}: {}\n'.format(thread_name, task_name )
    formated_string += '}'
    return formated_string


def get_formated_ressource_usage():
    return "Current RAM usage: {} MB".format(
        global_process.memory_info()[0] // 1000000
    )


class NonFatalExeption(Exception):
    pass


class GlobalStopFlag(Exception):
    pass


class MailReportableException(Exception):
    def __init__(self, title, message):
        self.title = title
        self.message = message
        super().__init__("An Error has to be reported by mail: %s" % title)


class MailReportableNonFatalException(MailReportableException, NonFatalExeption):
    pass
