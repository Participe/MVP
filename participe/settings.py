#Django settings for participe project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates/'),
    )

ADMINS = (
    ('OVERRIDE ME IN LOCAL_SETTINGS', 'OVERRIDE ME IN LOCAL_SETTINGS'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', u'English'),
    ('de', u'Deutsch'),
    ('fr', u'Fran\xe7ais'),
    ('it', u'Italiano'),
)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_PATH , 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_PATH , 'static')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1jx6w0srz51710=4szm_9!-31pofisn1zvkw7437b@tav88sue'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.csrf",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auth_remember.middleware.AuthRememberMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # The HTTP 403 exception
    'participe.core.middleware.Http403Middleware',
    'participe.core.middleware.Http501Middleware',
)

ROOT_URLCONF = 'participe.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'participe.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.flatpages',

    'south',
    'social_auth',
    'captcha',
    'easy_thumbnails',
    'auth_remember',
    'django_extensions', #for shell_plus and runserver_plus

    'participe.core',
    'participe.home',
    'participe.challenge',
    'participe.organization',
    'participe.account',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Put here the proper domain name. For testing needs this value could be
# overriden in local_settings.py (or not)
DOMAIN_NAME = "beta.partici.pe"

###############################################################################
### DJANGO CELERY AND MESSAGE BROKER SECTION                                ###
###############################################################################
import djcelery
djcelery.setup_loader()

INSTALLED_APPS += (
        "djcelery",
        "djkombu",)

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_IMPORTS = (
        "participe.challenge.tasks",)

###############################################################################
### DJANGO EASY THUMBNAILS SECTION                                          ###
###############################################################################
THUMBNAIL_ALIASES = {
    '': {
            'span2_thumb': {
                'size': (130, 60),
                'crop': "smart",
                'upscale': True,
            },
            'span4_thumb': {
                'size': (370, 210),
                'crop': "smart",
                'upscale': True,
            },
            'span3_large': {
                'size': (220, 220),
                'crop': "smart",
                'upscale': True,
            },
            'span9_wide': {
                'size': (830, 220),
                'crop': "smart",
                'upscale': True,
            },
            'span6_wide': {
                'size': (570, 420),
                'crop': "smart",
                'upscale': True,
            },
            'span12_wide': {
                'size': (1170, 200),
                'crop': "smart",
                'upscale': True,
            },
    },
}

###############################################################################
### DJANGO AVATAR (CROP) SECTION                                            ###
###############################################################################
AVATAR_DEFAULT_SIZE = 80
AVATAR_ALLOWED_FILE_EXTS = [".jpg", ".jpeg", ".png",]
AVATAR_MAX_SIZE = 5*1024*1024
AVATAR_MAX_AVATARS_PER_USER = 1

AVATAR_THUMB_FORMAT = "JPEG"
AVATAR_THUMB_QUALITY = 85

AVATAR_CROP_MAX_SIZE = 500
AVATAR_CROP_MIN_SIZE = 15

###############################################################################
### DJANGO SOCIAL AUTH SECTION                                              ###
###############################################################################
AUTHENTICATION_BACKENDS = (
    #'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.google.GoogleBackend',
    #'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.browserid.BrowserIDBackend',
    #'social_auth.backends.contrib.linkedin.LinkedinBackend',
    #'social_auth.backends.contrib.disqus.DisqusBackend',
    #'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #'social_auth.backends.contrib.orkut.OrkutBackend',
    #'social_auth.backends.contrib.foursquare.FoursquareBackend',
    #'social_auth.backends.contrib.github.GithubBackend',
    #'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    #'social_auth.backends.contrib.live.LiveBackend',
    #'social_auth.backends.contrib.skyrock.SkyrockBackend',
    #'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    #'social_auth.backends.OpenIDBackend',
    'participe.core.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'auth_remember.backend.AuthRememberBackend',
)

#TODO Override this in local_settings.py
#TWITTER_CONSUMER_KEY         = ''
#TWITTER_CONSUMER_SECRET      = ''
FACEBOOK_APP_ID              = '435671289832919'
FACEBOOK_API_SECRET          = 'f892e1490d357d6ebb8392c7c7b8c54d'
FACEBOOK_EXTENDED_PERMISSIONS = [
    #'user_about_me', 'user_activities',
    'user_birthday',
    #'user_checkins', 'user_education_history', 'user_events',
    #'user_groups', 'user_hometown', 'user_interests', 'user_likes',
    'user_location',
    #'user_notes', 'user_photos', 'user_questions',
    #'user_relationships', 'user_relationship_details',
    #'user_religion_politics', 'user_status', 'user_subscriptions',
    #'user_videos', 'user_website', 'user_work_history',
    'email',]
#LINKEDIN_CONSUMER_KEY        = ''
#LINKEDIN_CONSUMER_SECRET     = ''
#ORKUT_CONSUMER_KEY           = ''
#ORKUT_CONSUMER_SECRET        = ''
#GOOGLE_CONSUMER_KEY          = ''
#GOOGLE_CONSUMER_SECRET       = ''
#GOOGLE_OAUTH2_CLIENT_ID      = ''
#GOOGLE_OAUTH2_CLIENT_SECRET  = ''
#FOURSQUARE_CONSUMER_KEY      = ''
#FOURSQUARE_CONSUMER_SECRET   = ''
#VK_APP_ID                    = ''
#VK_API_SECRET                = ''
#LIVE_CLIENT_ID               = ''
#LIVE_CLIENT_SECRET           = ''
#SKYROCK_CONSUMER_KEY         = ''
#SKYROCK_CONSUMER_SECRET      = ''
#YAHOO_CONSUMER_KEY           = ''
#YAHOO_CONSUMER_SECRET        = ''

LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/view/'
LOGIN_ERROR_URL    = '/login-error/'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/accounts/profile/view/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/accounts/profile/edit/'
#SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = ''
#SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = ''
#SOCIAL_AUTH_BACKEND_ERROR_URL = ''

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

TEMPLATE_CONTEXT_PROCESSORS += (
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

import random
SOCIAL_AUTH_DEFAULT_USERNAME = lambda: random.choice(
    ['Darth Vader', 'Obi-Wan Kenobi', 'R2-D2', 'C-3PO', 'Yoda',
    'Luke Skywalker',])

#SOCIAL_AUTH_UUID_LENGTH = 16
#SOCIAL_AUTH_EXTRA_DATA = False

#SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email',]
#SOCIAL_AUTH_EXPIRATION = 'expires'
#SOCIAL_AUTH_SESSION_EXPIRATION = False

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',

    'participe.core.auth_pipelines.get_user_avatar',
    'participe.core.auth_pipelines.get_extra_data',
)

AUTH_PROFILE_MODULE = 'account.UserProfile'

###############################################################################
### "Remember me"                                                           ###
###############################################################################
AUTH_REMEMBER_COOKIE_NAME = 'remember_token'
AUTH_REMEMBER_COOKIE_AGE = 365 * 24 * 60 * 60 # 1 year
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

###############################################################################
###                                                                         ###
###############################################################################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'OVERRIDE ME IN LOCAL_SETTINGS'
EMAIL_HOST_PASSWORD= 'OVERRIDE ME IN LOCAL_SETTINGS'
EMAIL_HOST = 'OVERRIDE ME IN LOCAL_SETTINGS'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'
TEMPLATED_EMAIL_TEMPLATE_DIR = 'emails/'
TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

# Override some settings
try:
    from local_settings import *
except:
    pass
