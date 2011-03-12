from django.conf.urls.defaults import *
from django.core.urlresolvers import RegexURLPattern

from transurlvania.urlresolvers import LangSelectionRegexURLResolver
from transurlvania.urlresolvers import MultilangRegexURLResolver
from transurlvania.urlresolvers import MultilangRegexURLPattern
from transurlvania.urlresolvers import PocketURLModule


def lang_prefixed_patterns(prefix, *args):
    pattern_list = patterns(prefix, *args)
    return [LangSelectionRegexURLResolver(PocketURLModule(pattern_list))]


def url(regex, view, kwargs=None, name=None, prefix=''):
    # Copied from django.conf.urls.defaults.url
    if isinstance(view, (list,tuple)):
        # For include(...) processing.
        urlconf_module, app_name, namespace = view
        return MultilangRegexURLResolver(regex, urlconf_module, kwargs, app_name=app_name, namespace=namespace)
    else:
        if isinstance(view, basestring):
            if not view:
                raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return MultilangRegexURLPattern(regex, view, kwargs, name)

# Copied from django.conf.urls.defaults so that it's invoking the url func
# defined here instead of the built-in one.
def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list
