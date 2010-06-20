from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language

from transurlvania.settings import LANGUAGE_DOMAINS


def complete_url(url, lang=None):
    """
    Takes a url (or path) and returns a full url including the appropriate
    domain name (based on the LANGUAGE_DOMAINS setting).
    """
    if not url.startswith('http://'):
        lang = lang or get_language()
        domain = LANGUAGE_DOMAINS.get(lang)
        if domain:
            url = u'http://%s%s' % (domain[0], url)
        else:
            raise ImproperlyConfigured(
                'Not domain specified for language code %s' % lang
            )
    return url
