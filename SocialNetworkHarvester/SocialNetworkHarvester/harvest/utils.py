import time

from SocialNetworkHarvester.harvest.globals import start_time, global_thread_stop_flag


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
