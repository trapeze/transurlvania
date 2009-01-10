from django.conf import settings
from django.utils import translation


class LangInURLMiddleware(object):
    """
    Middleware for determining site's language via a language code in the URL
    This needs to be installed after the LocaleMiddleware so it can override that
    middleware's decisions.
    """
    def __init__(self):
        self.lang_codes = set(dict(settings.LANGUAGES).keys())

    def process_request(self, request):
        potential_lang_code = request.path_info.lstrip('/').split('/', 1)[0]
        if potential_lang_code in self.lang_codes:
            translation.activate(potential_lang_code)
            request.LANGUAGE_CODE = translation.get_language()
