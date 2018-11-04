import importlib
import inspect
import os
import time

from django.utils.timezone import now
from django_extensions.management.jobs import BaseJob

from SocialNetworkHarvester.harvest import BaseTaskProducer
from SocialNetworkHarvester.harvest.globals import global_errors, global_thread_stop_flag, global_task_queue, \
    global_process
from SocialNetworkHarvester.harvest.taskConsumer import TaskConsumer
from SocialNetworkHarvester.harvest.utils import (
    MailReportableException,
    get_running_time_in_minutes,
    get_running_time_in_seconds, get_running_time_in_hours, get_formated_ressource_usage, get_formated_thread_list)
from SocialNetworkHarvester.loggers.jobsLogger import log, logError, mail_log
from SocialNetworkHarvester.settings import HARVEST_APPS, DEBUG, LOG_DIRECTORY, TASK_CONSUMERS_COUNT, \
    MONITORING_DELAY_IN_SECONDS, MAX_RAM_USAGE_LIMIT_IN_MEGABYTE

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
    time.sleep(MONITORING_DELAY_IN_SECONDS)
    while True:
        if not global_errors.empty():
            thread, error = global_errors.get()
            log('ERROR OCCURED IN THREAD: {}'.format(thread))
            manage_exception(error)
        if global_process.memory_info()[0] // 1000000 > MAX_RAM_USAGE_LIMIT_IN_MEGABYTE:
            raise MaxRAMUsageLimitReachedException
        display_jobs_statuses()
        time.sleep(MONITORING_DELAY_IN_SECONDS)


def display_jobs_statuses():
    with open(os.path.join(LOG_DIRECTORY, 'harvest_job_tasks_status.log'), 'w') as f:
        f.write('\n' * 20)
        f.write(
            '####  HARVEST STATUS  ####\n'
            'Last updated: {last_updated:%Y/%m/%d %H:%M}\n'
            'Current running time: {running_time_hour} hours '
            '{running_time_minute} minutes {running_time_second} seconds\n'
            '{ressource_usage}\n'
            '{task_queue}\n'
            '{thread_list}\n'.format(
                last_updated=now(),
                running_time_hour=int(get_running_time_in_hours()),
                running_time_minute=int(get_running_time_in_minutes() % 3600),
                running_time_second=int(get_running_time_in_seconds() % 60),
                ressource_usage=get_formated_ressource_usage(),
                task_queue=global_task_queue.formated_tasks_counts(),
                thread_list=get_formated_thread_list(threads_list[0]),
            ))


def manage_exception(error):
    if isinstance(error, MailReportableException):
        logError("A reportable-by-mail error has occured")
        if not DEBUG:
            mail_log('Aspira Harvest Error - %s' % error.title, error.message)
        monitor_progress()
    else:
        end_threads()
        raise error


def end_threads():
    log('Ending all threads.')
    global_thread_stop_flag[0] = True
    for thread in threads_list[0]:
        if thread.is_alive():
            log('Joining thread %s' % thread.name)
            thread.join(timeout=3)
    log('Successfully joined all threads')


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
        except MaxRAMUsageLimitReachedException:
            logError("Max RAM usage limit reached {} Mb. Restarting".format(
                MAX_RAM_USAGE_LIMIT_IN_MEGABYTE
            ))
            end_threads()
            global_task_queue.clear()
            return self.execute()
        except Exception:
            end_threads()
            msg = "An unknown exception occured while harvesting data."
            logError(msg)
            if DEBUG:
                raise
            else:
                mail_log('Aspira - Harvest Unknown Error', msg)
        log('harvest ended')


class MaxRAMUsageLimitReachedException(Exception):
    pass
