import os

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(os.path.dirname(__file__), 'transurlvania_test.db')

LANGUAGE_CODE = 'en'

gettext = lambda s: s

LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('de', gettext('German')),
)

MULTILANG_LANGUAGE_DOMAINS = {
    'en': ('www.trapeze-en.com', 'English Site'),
    'fr': ('www.trapeze-fr.com', 'French Site')
}

MIDDLEWARE_CLASSES = (
    'transurlvania.middleware.URLCacheResetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'transurlvania.middleware.LangInPathMiddleware',
    'transurlvania.middleware.LangInDomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'transurlvania.middleware.URLTransMiddleware',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'transurlvania.context_processors.translate',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'transurlvania',
    'garfield',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates/'),
)
