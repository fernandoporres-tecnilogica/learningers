# -*- coding: utf-8 -*-
"""
Django settings for learningers project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: learningers.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&t7i2jfuzmy^q3z)7vd0y0_w!1u_=*c6j3p43act_&qi=jlg+0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages",
    "learningers.context_processors.login_form",
    )

AUTHENTICATION_BACKENDS = (
 'django.contrib.auth.backends.ModelBackend',
 'lazysignup.backends.LazySignupBackend',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # for user registration
    'registration',
    'lazysignup',
    # for searching
    'haystack',
    # for versioning
    'reversion',
    # for autocomplete
    'ajax_select',
    # for axhwsulinf of events
    'recurrence',
    # for geolocalisation
    'django.contrib.gis',
    # for model forking
    'forkit',
    # various model utilities
    'model_utils',
    # for migrations
    'south',
    # for translation
    'django_languages',
    # for in-place editing
    'inplaceeditform',
    'inplaceeditform_extra_fields',
    'django_markdown',
    # our apps
    'learningers',
    'catalog',
    'commons',
    'formfield',
    # for running custom scripts
     'django_extensions',
    # for documentation
     'giza',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'catalog.middleware.ParcoursSessionMiddleware',
)

ROOT_URLCONF = 'learningers.urls'

WSGI_APPLICATION = 'learningers.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
       'ENGINE': 'django.contrib.gis.db.backends.spatialite',
       'NAME': os.path.join(BASE_DIR, '/home/rnguyen/db.sqlite3'),
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

LANGUAGES = (
    ('fr', _(u'Français')),
    ('en', _('Anglais')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#######################
#     APP SETTINGS    #
#######################

# HAYSTACK
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# REGISTRATION
ACCOUNT_ACTIVATION_DAYS = 7

# AJAX_SELECT
# for autocomplete
AJAX_LOOKUP_CHANNELS = {
    'city' : ('learningers.lookups','CityLookup'),
    'way' : ('catalog.lookups','WayLookup'),
 }

## Email conf
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'romain.nguyenvanyen@gmail.com'
EMAIL_HOST_PASSWORD = 'ceumdpd9c'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = True

# In-place edit
#for in-place edit
INPLACEEDIT_EDIT_EMPTY_VALUE = _(u'Insérer...')
INPLACEEDIT_AUTO_SAVE = True
INPLACEEDIT_EVENT = "dblclick"
INPLACEEDIT_DISABLE_CLICK = False  # For inplace edit text into a link tag
INPLACEEDIT_EDIT_MESSAGE_TRANSLATION = 'Write a translation' # transmeta option
INPLACEEDIT_SUCCESS_TEXT = _(u'Enregistré')
INPLACEEDIT_UNSAVED_TEXT = _(u'Il y a des modifications non-enregistrées')
ADAPTOR_INPLACEEDIT_EDIT = 'learningers.perms.MyAdaptorEditInline'
ADAPTOR_INPLACEEDIT = {
                       'html': 'inplaceeditform.fields.AdaptorTextAreaField',
                       'm2mcomma': 'inplaceeditform_extra_fields.fields.AdaptorAutoCompleteManyToManyField',
                       }
# Giza conf
GIZA_DOCS_ROOT = '/home/rnguyen/cpp/learningers/doc/source'

