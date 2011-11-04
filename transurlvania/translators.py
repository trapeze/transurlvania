from django.core.urlresolvers import NoReverseMatch

from transurlvania.urlresolvers import reverse_for_language


class NoTranslationError(Exception):
    pass


class ViewInfo(object):
    def __init__(self, current_url, view_func, view_args, view_kwargs):
        self.current_url = current_url
        self.view_func = view_func
        self.view_args = view_args
        self.view_kwargs = view_kwargs

    def __unicode__(self):
        return 'URL:%s, handled by %s(*%s, **%s)' % (self.current_url,
            self.view_func, self.view_args, self.view_kwargs)

class BasicScheme(object):
    def get_url(self, lang, view_info, context=None):
        "The basic translation scheme just returns the current URL"
        return view_info.current_url


class ObjectBasedScheme(BasicScheme):
    """
    Translates by finding the specified object in the context dictionary,
    getting that object's translation in teh requested language, and
    returning the object's URL.
    """

    DEFAULT_OBJECT_NAME = 'object'

    def __init__(self, object_name=None):
        self.object_name = object_name or self.DEFAULT_OBJECT_NAME

    def get_url(self, lang, view_info, context=None):
        try:
            return context[self.object_name].get_translation(lang).get_absolute_url()
        except KeyError:
            raise NoTranslationError(u'Could not find object named %s in context.' % self.object_name)
        except AttributeError:
            raise NoTranslationError(u'Unable to get translation of object %s '
                                     u'in language %s' % (context[self.object_name], lang))


class DirectToURLScheme(BasicScheme):
    """
    Translates using a view function (or URL name) and the args and kwargs that
    need to be passed to it. The URL is found by doing a reverse lookup for the
    specified view in the requested language.
    """

    def __init__(self, url_name=None):
        self.url_name = url_name

    def get_url(self, lang, view_info, context=None):
        view_func = self.url_name or view_info.view_func
        try:
            return reverse_for_language(view_func, lang, None,
                view_info.view_args, view_info.view_kwargs)
        except NoReverseMatch:
            raise NoTranslationError('Unable to find URL for %s' % view_func)


class AutodetectScheme(BasicScheme):
    """
    Tries to translate using an "object" entry in the context, or, failing
    that, tries to find the URL for the view function it was given in the
    requested language.
    """
    def __init__(self, object_name=None):
        self.object_translator = ObjectBasedScheme(object_name)
        self.view_translator = DirectToURLScheme()

    def get_url(self, lang, view_info, context=None):
        """
        Tries translating with the object based scheme and falls back to the
        direct-to-URL based scheme if that fails.
        """
        try:
            return self.object_translator.get_url(lang, view_info, context)
        except NoTranslationError:
            try:
                return self.view_translator.get_url(lang, view_info, context)
            except NoTranslationError:
                return super(AutodetectScheme, self).get_url(lang, view_info, context)


class URLTranslator(object):
    def __init__(self, current_url, scheme=None):
        self.scheme = scheme or BasicScheme()
        self.view_info = ViewInfo(current_url, None, None, None)

    def set_view_info(self, view_func, view_args, view_kwargs):
        self.view_info.view_func = view_func
        self.view_info.view_args = view_args
        self.view_info.view_kwargs = view_kwargs

    def __unicode__(self):
        return 'URL Translator for %s. Using scheme: %s.' % (self.view_info,
                                                             self.scheme)

    def get_url(self, lang, context=None):
        return self.scheme.get_url(lang, self.view_info, context)