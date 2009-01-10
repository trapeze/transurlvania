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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'multilang.middleware.LangInURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'multilang.tests.lang_prefixed_urls'

INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'multilang',
        'multilang.tests',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates/'),
)

AUTH_PROFILE_MODULE = "profiles.userprofile"
