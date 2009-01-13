from django.conf import settings
from django.utils import translation

from multilang.translators import URLTranslator, AutodetectScheme


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


class MultilangMiddleware(object):
    def process_request(self, request):
        request.url_translator = URLTranslator(request.build_absolute_uri())

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.url_translator.set_view_info(view_func, view_args, view_kwargs)
        request.url_translator.scheme = AutodetectScheme()
        return None


class BlockLocaleMiddleware(object):
    """
    This middleware will prevent users from accessing the site in a specified
    list of languages unless the user is authenticated and a staff member.
    It should be installed below LocaleMiddleware and AuthenticationMiddleware.
    """
    def __init__(self):
        self.default_lang = settings.LANGUAGE_CODE
        self.blocked_langs = set(getattr(settings, 'BLOCKED_LANGUAGES', []))

    def process_request(self, request):
        lang = getattr(request, 'LANGUAGE_CODE', None)
        if lang in self.blocked_langs and (not hasattr(request, 'user') or not request.user.is_staff):
            request.LANGUAGE_CODE = self.default_lang
            translation.activate(self.default_lang)
