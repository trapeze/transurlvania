import re

from django.conf import settings
from django.conf.urls.defaults import handler404, handler500
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, get_callable
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import get_script_prefix
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import iri_to_uri, force_unicode
from django.utils.regex_helper import normalize
from django.utils.translation import get_language
from django.utils.translation.trans_real import translation

import transurlvania.settings


_resolvers = {}
def get_resolver(urlconf, lang):
    if urlconf is None:
        from django.conf import settings
        urlconf = settings.ROOT_URLCONF
    key = (urlconf, lang)
    if key not in _resolvers:
        _resolvers[key] = MultilangRegexURLResolver(r'^/', urlconf)
    return _resolvers[key]


def reverse_for_language(viewname, lang, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    # Based on code in Django 1.1.1 in reverse and RegexURLResolver.reverse 
    # in django.core.urlresolvers.
    args = args or []
    kwargs = kwargs or {}
    if prefix is None:
        prefix = get_script_prefix()
    resolver = get_resolver(urlconf, lang)

    if not isinstance(viewname, basestring):
        view = viewname
    else:
        parts = viewname.split(':')
        parts.reverse()
        view = parts[0]
        path = parts[1:]

        resolved_path = []
        while path:
            ns = path.pop()

            # Lookup the name to see if it could be an app identifier
            try:
                app_list = resolver.app_dict[ns]
                # Yes! Path part matches an app in the current Resolver
                if current_app and current_app in app_list:
                    # If we are reversing for a particular app, use that namespace
                    ns = current_app
                elif ns not in app_list:
                    # The name isn't shared by one of the instances (i.e., the default)
                    # so just pick the first instance as the default.
                    ns = app_list[0]
            except KeyError:
                pass

            try:
                extra, resolver = resolver.namespace_dict[ns]
                resolved_path.append(ns)
                prefix = prefix + extra
            except KeyError, key:
                if resolved_path:
                    raise NoReverseMatch("%s is not a registered namespace inside '%s'" % (key, ':'.join(resolved_path)))
                else:
                    raise NoReverseMatch("%s is not a registered namespace" % key)

    if args and kwargs:
        raise ValueError("Don't mix *args and **kwargs in call to reverse()!")
    try:
        lookup_view = get_callable(view, True)
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
                iri = u'%s%s' % (prefix, candidate)
                # If we have a separate domain for lang, put that in the iri
                domain = transurlvania.settings.LANGUAGE_DOMAINS.get(lang, None)
                if domain:
                    iri = u'http://%s%s' % (domain[0], iri)
                return iri_to_uri(iri)
    # lookup_view can be URL label, or dotted path, or callable, Any of
    # these can be passed in at the top, but callables are not friendly in
    # error messages.
    m = getattr(lookup_view, '__module__', None)
    n = getattr(lookup_view, '__name__', None)
    if m is not None and n is not None:
        lookup_view_s = "%s.%s" % (m, n)
    else:
        lookup_view_s = lookup_view
    raise NoReverseMatch("Reverse for '%s' with arguments '%s' and keyword "
            "arguments '%s' not found." % (lookup_view_s, args, kwargs))


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
    def __init__(self, regex, urlconf_name, default_kwargs=None, app_name=None, namespace=None):
        # regex is a string representing a regular expression.
        # urlconf_name is a string representing the module containing urlconfs.
        self._raw_regex = regex
        self.urlconf_name = urlconf_name
        if not isinstance(urlconf_name, basestring):
            self._urlconf_module = self.urlconf_name
        self.callback = None
        self.default_kwargs = default_kwargs or {}
        self.namespace = namespace
        self.app_name = app_name
        self._lang_reverse_dicts = {}
        self._namespace_dict = None
        self._app_dict = None
        self._regex_dict = {}

    def get_regex(self, lang=None):
        lang = lang or get_language()
        # Only attempt to get the translation of the regex if the regex string
        # is not empty. The empty string is handled as a special case by
        # Django's gettext. It's where it stores its metadata.
        if self._raw_regex != '':
            regex_in_lang = translation(lang).ugettext(self._raw_regex)
        else:
            regex_in_lang = self._raw_regex
        return self._regex_dict.setdefault(lang, re.compile(regex_in_lang, re.UNICODE))
    regex = property(get_regex)

    def _build_reverse_dict_for_lang(self, lang):
        reverse_dict = MultiValueDict()
        namespaces = {}
        apps = {}
        for pattern in reversed(self.url_patterns):
            if hasattr(pattern, 'get_regex'):
                p_pattern = pattern.get_regex(lang).pattern
            else:
                p_pattern = pattern.regex.pattern
            if p_pattern.startswith('^'):
                p_pattern = p_pattern[1:]
            if isinstance(pattern, RegexURLResolver):
                if pattern.namespace:
                    namespaces[pattern.namespace] = (p_pattern, pattern)
                    if pattern.app_name:
                        apps.setdefault(pattern.app_name, []).append(pattern.namespace)
                else:
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
                    for namespace, (prefix, sub_pattern) in pattern.namespace_dict.items():
                        namespaces[namespace] = (p_pattern + prefix, sub_pattern)
                    for app_name, namespace_list in pattern.app_dict.items():
                        apps.setdefault(app_name, []).extend(namespace_list)
            else:
                bits = normalize(p_pattern)
                reverse_dict.appendlist(pattern.callback, (bits, p_pattern))
                reverse_dict.appendlist(pattern.name, (bits, p_pattern))
        self._namespace_dict = namespaces
        self._app_dict = apps
        return reverse_dict

    def get_reverse_dict(self, lang=None):
        if lang is None:
            lang = get_language()
        if lang not in self._lang_reverse_dicts:
            self._lang_reverse_dicts[lang] = self._build_reverse_dict_for_lang(lang)
        return self._lang_reverse_dicts[lang]
    reverse_dict = property(get_reverse_dict)


class LangSelectionRegexURLResolver(MultilangRegexURLResolver):
    def __init__(self, urlconf_name, default_kwargs=None, app_name=None, namespace=None):
        # urlconf_name is a string representing the module containing urlconfs.
        self.urlconf_name = urlconf_name
        if not isinstance(urlconf_name, basestring):
            self._urlconf_module = self.urlconf_name
        self.callback = None
        self.default_kwargs = default_kwargs or {}
        self.namespace = namespace
        self.app_name = app_name
        self._lang_reverse_dicts = {}
        self._namespace_dict = None
        self._app_dict = None
        self._regex_dict = {}

    def get_regex(self, lang=None):
        lang = lang or get_language()
        return re.compile('^%s/' % lang)
    regex = property(get_regex)


class PocketURLModule(object):
    handler404 = handler404
    handler500 = handler500

    def __init__(self, pattern_list):
        self.urlpatterns = pattern_list

