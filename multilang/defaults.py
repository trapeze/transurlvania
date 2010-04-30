from django.conf.urls.defaults import *

from multilang.urlresolvers import LangSelectionRegexURLResolver
from multilang.urlresolvers import MultilangRegexURLResolver
from multilang.urlresolvers import MultilangRegexURLPattern


def lang_prefixed(urlconf_name):
    return LangSelectionRegexURLResolver(urlconf_name)


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
