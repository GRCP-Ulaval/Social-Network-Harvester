import importlib
import inspect
import time

from django_extensions.management.jobs import BaseJob

from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.globals import global_errors, global_thread_stop_flag
from SocialNetworkHarvester.harvest.taskConsumer import TaskConsumer
from SocialNetworkHarvester.harvest.utils import MailReportableException
from SocialNetworkHarvester.loggers.jobsLogger import log, logError, mail_log
from SocialNetworkHarvester.settings import HARVEST_APPS, DEBUG

TASK_CONSUMERS_COUNT = 10

threads_list = [[]]


def parse_harvest_modules():
    task_producers = []
    for app in HARVEST_APPS:
        try:
            module = importlib.import_module('%s.harvest.task_producers' % app)
        except ModuleNotFoundError:
            raise ModuleNotFoundError('You must create a module named "harvest.task_producers" inside app %s' % app)
        task_producers += inspect.getmembers(
            module, lambda c: inspect.isclass(c) and issubclass(c, BaseTaskProducer)
        )
    return [i[1] for i in task_producers]


def generate_consumers():
    for i in range(1, TASK_CONSUMERS_COUNT + 1):
        t = TaskConsumer(name="Task Consumer #%i" % i)
        threads_list[0].append(t)
        t.start()


def generate_producers():
    for Producer in parse_harvest_modules():
        t = Producer()
        threads_list[0].append(t)
        t.start()


def monitor_progress():
    while True:
        if not global_errors.empty():
            thread, error = global_errors.get()
            log('Error occured in thread: %s' % thread.name)
            manage_exception(error)
        time.sleep(3)


def manage_exception(error):
    if isinstance(error, MailReportableException):
        logError("A reportable-by-mail error has occured")
        if not DEBUG:
            mail_log('Aspira Harvest Error - %s' % error.title, error.message)
        monitor_progress()
    else:
        raise error


def end_threads():
    log('Ending all threads.')
    global_thread_stop_flag[0] = True
    for thread in threads_list[0]:
        if thread.is_alive():
            thread.join()


class Job(BaseJob):
    name = 'harvest_data'
    help = 'Harvest data from specified modules specified in HARVEST_APPS'
    when = 'unscheduled'
    task_consumers_count = 1

    def __init__(self, *args, **kwargs):
        super(Job).__init__(*args, **kwargs)

    def execute(self):
        try:
            log('New job started.\n\n')
            log('Running job: "{}"'.format(self.name))
            generate_consumers()
            generate_producers()
            monitor_progress()
            log('Job "{}" has completed.'.format(self.name))
        except Exception:
            end_threads()
            msg = "An unknown exception occured while harvesting data."
            logError(msg)
            if not DEBUG:
                mail_log('Aspira - Harvest Unknown Error', msg)
        log('harvest ended')
