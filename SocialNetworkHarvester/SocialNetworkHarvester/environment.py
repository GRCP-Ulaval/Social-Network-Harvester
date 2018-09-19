import os


def get_from_env(variable_name, default=None, prefix=None):
    prefix = '{}_'.format(prefix) if prefix else ''
    return os.environ.get('{}{}'.format(prefix, variable_name), default)


SECRET_KEY = get_from_env('DJANGO_SECRET_KEY', default='123abc')
DEBUG = get_from_env('DJANGO_DEBUG', default=True) not in ['0', 'false', 'False']
FACEBOOK_APP_PARAMS = {
    'app_id': get_from_env('DJANGO_FB_APP_ID'),
    'version': get_from_env('DJANGO_FB_APP_VERSION'),
    'secret_key': get_from_env('DJANGO_FB_APP_SECRET')}

YOUTUBE_VIDEOS_LOCATION = ''  # Absolute path to folder

# Email settings
EMAIL_HOST = get_from_env('DJANGO_EMAIL_HOST')
EMAIL_HOST_USER = get_from_env('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_from_env('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True
EMAIL_PORT = 465

# Database settings
DATABASE_PARAMS = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': get_from_env('DJANGO_DB_NAME'),
    'USER': get_from_env('DJANGO_DB_USER'),
    'PASSWORD': get_from_env('DJANGO_DB_PASSWORD'),
    'HOST': get_from_env('DJANGO_DB_HOST', '127.0.0.1'),
    'PORT': get_from_env('DJANGO_DB_HOST', '3306'),
}
