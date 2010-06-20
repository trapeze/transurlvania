from django.conf import settings
from django.core import urlresolvers
from django.utils import translation

from transurlvania.settings import LANGUAGE_DOMAINS
from transurlvania.translators import URLTranslator, AutodetectScheme


class LangInPathMiddleware(object):
    """
    Middleware for determining site's language via a language code in the path
    This needs to be installed after the LocaleMiddleware so it can override
    that middleware's decisions.
    """
    def __init__(self):
        self.lang_codes = set(dict(settings.LANGUAGES).keys())

    def process_request(self, request):
        potential_lang_code = request.path_info.lstrip('/').split('/', 1)[0]
        if potential_lang_code in self.lang_codes:
            translation.activate(potential_lang_code)
            request.LANGUAGE_CODE = translation.get_language()


class LangInDomainMiddleware(object):
    """
    Middleware for determining site's language via the domain name used in
    the request.
    This needs to be installed after the LocaleMiddleware so it can override
    that middleware's decisions.
    """

    def process_request(self, request):
        for lang in LANGUAGE_DOMAINS.keys():
            if LANGUAGE_DOMAINS[lang][0] == request.META['SERVER_NAME']:
                translation.activate(lang)
                request.LANGUAGE_CODE = translation.get_language()


class URLTransMiddleware(object):
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


class URLCacheResetMiddleware(object):
    """
    Middleware that resets the URL resolver cache after each response.

    Install this as the first middleware in the list so it gets run last as the
    response goes out. It will clear the URLResolver cache. The cache needs to
    be cleared between requests because the URLResolver objects in the cache
    are locked into one language, and the next request might be in a different
    language.

    This middleware is required if the project uses translated URLs.
    """
    def process_response(self, request, response):
        urlresolvers.clear_url_caches()
        return response
