from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# We need to wrap the language description in the real ugettext if we
# want the translation to be available.

LANGUAGES_CHOICES = [
        (code, _(description)) for (code, description) in settings.LANGUAGES
        ]