# IMPORTANT: copy this file into "environment.py" and then populate the values.

SECRET_KEY = ''
DEBUG = True
FACEBOOK_APP_PARAMS = {
    'app_id': '',
    'version': '',
    'secret_key': ''
}

YOUTUBE_VIDEOS_LOCATION = ''  # Absolute path to folder

# Email settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_SSL = True
EMAIL_PORT = 465

# Database settings
DATABASE_PARAMS = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}

# Data Harvester Settings
TASK_CONSUMERS_COUNT = 10  # Number of threads for harvesting (recommended: Number of cpu core + 1)
MONITORING_DELAY_IN_SECONDS = 1  # Delay between harvest job monitoring routines (decrease to improve performance)
MAX_RAM_USAGE_LIMIT_IN_MEGABYTE = 600  # Max RAM usage in megabyte used by the harvesting service.
SENTRY_ID = ""  # URL of the sentry (error-reporting) service
