import os

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(os.path.dirname(__file__), 'multilang_test.db')

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
    'multilang.middleware.URLCacheResetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'multilang.middleware.LangInPathMiddleware',
    'multilang.middleware.LangInDomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'multilang.middleware.URLTransMiddleware',
)

ROOT_URLCONF = 'tests.lang_prefixed_urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'multilang.context_processors.translate',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'multilang',
    'garfield',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates/'),
)
