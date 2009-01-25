from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# We need to wrap the language description in the real ugettext if we
# want the translation of the language names to be available (in the admin for
# instance).

LANGUAGES_CHOICES = [
    (code, _(description)) for (code, description) in settings.LANGUAGES
]
