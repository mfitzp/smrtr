import os.path 

# Django settings for spenglr project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Martin Fitzpatrick', 'mfitzp@spenglr.com'),
     ('Cael Kay-Jackson', 'caelj@spenglr.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'spenglr'             # Or path to database file if using sqlite3.
DATABASE_USER = 'spenglr'             # Not used with sqlite3.
DATABASE_PASSWORD = 'mould'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u2y=71bj-k%-iubxq+gvtwo7__7#b2gr^^4ug)a4*uzy^c7d#m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.RequireLoginMiddleware',
)

ROOT_URLCONF = 'urls'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.comments',
# External Helpers
    'countries', # http://code.google.com/p/django-countries/   (0.1r3)
    'atomformat',   # http://github.com/pinax/atom-format (place atomformat.py in externals/, no subdir)
# Externals
    'registration', #http://www.bitbucket.org/ubernostrum/django-registration/wiki/
    'avatar', #http://github.com/rhec/django-avatar/ This version supports overriding the default gravatar
              #Original at: switch on fix #http://github.com/ericflo/django-avatar #'gravatar', #http://code.google.com/p/django-gravatar/
    'tagging',
    'notification', #http://github.com/jtauber/django-notification
    'wall',  #http://github.com/jtauber/django-wall
    'picklefield',  #http://github.com/shrubberysoft/django-picklefield
    #'friends', #http://github.com/jtauber/django-friends WATCHING THIS FOR READINESS
# Spenglr
    'core',
    'profiles',
    'network',
    'education',
    'questions',
    'resources',
    'sq',
)

CACHE_BACKEND = 'dummy:///'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request'
)

AUTH_PROFILE_MODULE = "profiles.userprofile"

ACCOUNT_ACTIVATION_DAYS = 5
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

FORCE_LOWERCASE_TAGS = True

# Spenglr constants

# +/1 Range between levels of difficulty
SQ_FAIR_RANGE = 20

SQ_UPPER_LIMIT = 200
SQ_LOWER_LIMIT = 0

SQ_READOFF_MARK = 50

SQ_PINNING_WEIGHT = 0.1

# External avatar app setting (storage under /media/avatar)
AVATAR_STORAGE_DIR = "avatar"
AVATAR_DEFAULT_URL = "/media/img/default_avatar.png"
AVATAR_GRAVATAR_BACKUP_DEFAULT = "http://www.spenglr.com/media/img/default_avatar.png"

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass