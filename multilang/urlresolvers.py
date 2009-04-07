import re

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, get_callable
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import get_script_prefix
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import iri_to_uri, force_unicode
from django.utils.regex_helper import normalize
from django.utils.translation import get_language
from django.utils.translation.trans_real import translation


def turl(regex, view, kwargs=None, name=None, prefix=''):
    # Copied from django.conf.urls.defaults.url
    if type(view) == list:
        # For include(...) processing.
        return MultilangRegexURLResolver(regex, view[0], kwargs)
    else:
        if isinstance(view, basestring):
            if not view:
                raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return MultilangRegexURLPattern(regex, view, kwargs, name)


_resolvers = {}
def get_resolver(urlconf, lang):
    if urlconf is None:
        from django.conf import settings
        urlconf = settings.ROOT_URLCONF
    key = (urlconf, lang)
    if key not in _resolvers:
        _resolvers[key] = MultilangRegexURLResolver(r'^/', urlconf)
    return _resolvers[key]


def reverse_for_language(viewname, lang, urlconf=None, args=None, kwargs=None, prefix=None):
    # Copied from Django 1.0 code in django.core.urlresolvers.RegexURLResolver.reverse
    args = args or []
    kwargs = kwargs or {}
    if prefix is None:
        prefix = get_script_prefix()
    resolver = get_resolver(urlconf, lang)

    if args and kwargs:
        raise ValueError("Don't mix *args and **kwargs in call to reverse()!")
    try:
        lookup_view = get_callable(viewname, True)
    except (ImportError, AttributeError), e:
        raise NoReverseMatch("Error importing '%s': %s." % (lookup_view, e))
    if hasattr(resolver, 'get_reverse_dict'):
        possibilities = resolver.get_reverse_dict(lang).getlist(lookup_view)
    else:
        possibilities = resolver.reverse_dict.getlist(lookup_view)
    for possibility, pattern in possibilities:
        for result, params in possibility:
            if args:
                if len(args) != len(params):
                    continue
                unicode_args = [force_unicode(val) for val in args]
                candidate =  result % dict(zip(params, unicode_args))
            else:
                if set(kwargs.keys()) != set(params):
                    continue
                unicode_kwargs = dict([(k, force_unicode(v)) for (k, v) in kwargs.items()])
                candidate = result % unicode_kwargs
            if re.search(u'^%s' % pattern, candidate, re.UNICODE):
                return iri_to_uri(u'%s%s' % (prefix, candidate))
    raise NoReverseMatch("Reverse for '%s' with arguments '%s' and keyword "
            "arguments '%s' not found." % (lookup_view, args, kwargs))


class MultilangRegexURLPattern(RegexURLPattern):
    def __init__(self, regex, callback, default_args=None, name=None):
        # Copied from django.core.urlresolvers.RegexURLPattern, with one change:
        # The regex here is stored as a string instead of as a compiled re object.
        # This allows the code to use the gettext system to translate the URL
        # pattern at resolve time.
        self._raw_regex = regex

        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback
        self.default_args = default_args or {}
        self.name = name
        self._regex_dict = {}

    def get_regex(self, lang=None):
        lang = lang or get_language()
        return self._regex_dict.setdefault(lang, re.compile(translation(lang).ugettext(self._raw_regex), re.UNICODE))
    regex = property(get_regex)


class MultilangRegexURLResolver(RegexURLResolver):
    def __init__(self, regex, urlconf_name, default_kwargs=None):
        # regex is a string representing a regular expression.
        # urlconf_name is a string representing the module containing urlconfs.
        self._raw_regex = regex
        self.urlconf_name = urlconf_name
        self.callback = None
        self.default_kwargs = default_kwargs or {}
        self._lang_reverse_dicts = {}
        self._regex_dict = {}

    def get_regex(self, lang=None):
        lang = lang or get_language()
        return self._regex_dict.setdefault(lang, re.compile(translation(lang).ugettext(self._raw_regex), re.UNICODE))
    regex = property(get_regex)

    def _build_reverse_dict_for_lang(self, lang):
        reverse_dict = MultiValueDict()
        if hasattr(self.urlconf_module, 'urlpatterns'):
            for pattern in reversed(self.urlconf_module.urlpatterns):
                if hasattr(pattern, 'get_regex'):
                    p_pattern = pattern.get_regex(lang).pattern
                else:
                    p_pattern = pattern.regex.pattern
                if p_pattern.startswith('^'):
                    p_pattern = p_pattern[1:]
                if isinstance(pattern, RegexURLResolver):
                    if hasattr(pattern, 'get_regex'):
                        parent = normalize(pattern.get_regex(lang).pattern)
                    else:
                        parent = normalize(pattern.regex.pattern)
                    if hasattr(pattern, 'get_reverse_dict'):
                        sub_reverse_dict = pattern.get_reverse_dict(lang)
                    else:
                        sub_reverse_dict = pattern.reverse_dict
                    for name in sub_reverse_dict:
                        for matches, pat in sub_reverse_dict.getlist(name):
                            new_matches = []
                            for piece, p_args in parent:
                                new_matches.extend([(piece + suffix, p_args + args) for (suffix, args) in matches])
                            reverse_dict.appendlist(name, (new_matches, p_pattern + pat))
                else:
                    bits = normalize(p_pattern)
                    reverse_dict.appendlist(pattern.callback, (bits, p_pattern))
                    reverse_dict.appendlist(pattern.name, (bits, p_pattern))
        return reverse_dict

    def get_reverse_dict(self, lang=None):
        if lang is None:
            lang = get_language()
        if lang not in self._lang_reverse_dicts:
            self._lang_reverse_dicts[lang] = self._build_reverse_dict_for_lang(lang)
        return self._lang_reverse_dicts[lang]
    reverse_dict = property(get_reverse_dict)
