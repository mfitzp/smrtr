import os.path 
import sys

# Django settings for smrtr project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Martin Fitzpatrick', 'mfitzp@smrtr.org'),
     ('Cael Kay-Jackson', 'caelj@smrtr.org'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'smrtr'             # Or path to database file if using sqlite3.
DATABASE_USER = 'smrtr'             # Not used with sqlite3.
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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware', 
    'pagination.middleware.PaginationMiddleware',
    'core.middleware.RequireLoginMiddleware',
)

ROOT_URLCONF = 'urls'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external'))

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
    #'atomformat',   # http://github.com/pinax/atom-format (place atomformat.py in externals/, no subdir, not actually an INSTALLED_APP
# Externals
    'registration', #http://www.bitbucket.org/ubernostrum/django-registration/wiki/
    'avatar', #http://github.com/rhec/django-avatar/ This version supports overriding the default gravatar
              #Original at: switch on fix #http://github.com/ericflo/django-avatar #'gravatar', #http://code.google.com/p/django-gravatar/
    'tagging',
    #'friends', #http://github.com/jtauber/django-friends WATCHING THIS FOR READINESS
    'notification', #http://github.com/jtauber/django-notification
    'wall',  #http://github.com/jtauber/django-wall
    'picklefield',  #http://github.com/shrubberysoft/django-picklefield
    'flowplayer', #http://github.com/mfitzp/django-flowplayer
    'haystack', #http://haystacksearch.org/ http://github.com/toastdriven/django-haystack/tree/master  + xapian-haystack
    'pagination', #http://code.google.com/p/django-pagination
    'messages', #http://code.google.com/p/django-messages/downloads/list  Private messaging application
# Smrtr
    'core',
    'profiles',
    'network',
    'education',
    'questions',
    'resources',
    'sq',
    'challenge',
)

CACHE_BACKEND = 'dummy:///'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.media',
    'messages.context_processors.inbox',
)

AUTH_PROFILE_MODULE = "profiles.userprofile"

ACCOUNT_ACTIVATION_DAYS = 5
LOGIN_PATH = '/accounts/' # All paths under here are still accessible when logged out - allows login/registration
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

FORCE_LOWERCASE_TAGS = True

AVATAR_STORAGE_DIR = "avatar"

FLOWPLAYER_CONFIG = {
                        'default' : 
                            { 'clip' : { 'autoPlay':'false' }, },
                    }

COUNTRIES_FLAG_PATH = 'img/flags/%s.png'

# Smrtr constants

# +/1 Range between levels of difficulty
SQ_FAIR_RANGE = 20
SQ_UPPER_LIMIT = 200
SQ_LOWER_LIMIT = 0
SQ_READOFF_MARK = 50
SQ_PINNING_WEIGHT = 0.1

# Challenges

CHALLENGES_MIN_ACTIVE = 5

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'xapian'

HAYSTACK_XAPIAN_PATH = os.path.dirname(os.path.abspath(__file__)) + '/search_index'

# Some global urls for redirecting users nicely, error, 'finished', etc.
SMRTR_FREE_TIME_URL = 'http://amanita-design.net/samorost-2/'
SMRTR_HAVE_BREAK_URL = 'http://www.popcap.com/games/free/pvz?mid=pvz_pcweb_en_full'

# Email settings: user/pass combination is stored in local settings for security
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_SUBJECT_PREFIX ='[smrtr]'
DEFAULT_FROM_EMAIL = 'noreply@smrtr.org'
SERVER_EMAIL = 'noreply@smrtr.org'

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
    
    
# The following paths are dependent on setting correct base MEDIA/MEDIAADMIN urls in localsettings
# External avatar app setting (storage under /media/avatar)
AVATAR_DEFAULT_URL = MEDIA_URL + "img/default_avatar.png"
AVATAR_GRAVATAR_BACKUP_DEFAULT = MEDIA_URL + "img/default_avatar.png"

# Flowplayer (audio/video output)
FLOWPLAYER_URL = MEDIA_URL + "flowplayer/flowplayer-3.2.2.swf"

