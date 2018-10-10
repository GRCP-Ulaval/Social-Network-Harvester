from django.contrib import messages


def add_info_message(request, info_message):
    messages.add_message(request, messages.INFO, info_message)


def add_error_messages(request, info_messages):
    for info_message in info_messages:
        add_info_message(request, info_message)


def add_error_message(request, error_message):
    messages.add_message(request, messages.ERROR, error_message)


def add_error_messages(request, error_messages):
    for error_message in error_messages:
        add_error_message(request, error_message)
