Multilang URLs
==============

Introduction
------------

This application provides a collection of URL-related utilities for
multi-lingual projects.

Features
--------

* **Localizable URLs** - the same page can have a different url in a different
  language. (eg /products/ can be /produits/ in French)

* **Language-in-Path** - a replacement for Django's language cookie that
  makes URLs language-specific by storing the language code in the URL path.

* **Language-in-Domain** - a replacement for Django's language cookie that
  makes URLs language-specific by mapping each domain for the site onto a
  language.


Installation
------------

* Add ``transurlvania`` to ``INSTALLED_APPS`` in your settings file

* Add the following middlewares to ``MIDDLEWARE_CLASSES`` in your settings file:

  * ``transurlvania.middleware.URLCacheResetMiddleware`` (must be before the
    ``SessionMiddleware``)

  * ``transurlvania.middleware.URLTransMiddleware`` (must be before the
	``CommonMiddleware`` in order for APPEND_SLASH to work)

* Add ``transurlvania.context_processors.translate`` to
  ``TEMPLATE_CONTEXT_PROCESSORS``.

Usage
-----

Localizing URLs
~~~~~~~~~~~~~~~

Replace the usual::

    from django.conf.urls.defaults import *

with::

    from transurlvania.defaults import *

You will need the ugettext_noop function if you want to mark any URL patterns
for localization::

    from django.utils.translation import ugettext_noop as _

To make an URL pattern localizable, first ensure that it is in the
``url(...)`` form, then wrap the URL pattern itself in a gettext function
call::

    url(_(r'^about-us/$'), 'about_us', name='about_us'),

Now, when you next run the ``makemessages`` management command, these URL
patterns will be collected in the .po file along with all the other
localizable strings.

Notes:

* because the strings in the po file are not raw strings, some regex
  characters will be escaped, so the URL patterns are sometimes less readable

* When providing a translation for a URL pattern that includes regex elements,
  ensure that the translation contains the same regex elements, otherwise the
  pattern matching behaviour may vary from language to language.

Localizing ``get_absolute_url``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any language-aware models that define ``get_absolute_url`` should decorate it
with ``permalink_in_lang``, from ``transurlvania.decorators`` so that the
returned URLs will be properly translated to the language of the object.
``permalink_in_lang`` accepts the same tuple values as ``permalink`` except
that the language code to be used for the URL should be inserted between the
name of the view or URL and the ``view_args`` parameter::

    @permalink_in_lang
    def get_absolute_url(self):
        ('name_of_view_or_url', self.language, (), {})


Making URLs Language-Specific
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

transurlvania provides two ways for making URLs language-specific, meaning that
the URL itself will indicate what language to use when generating the
response.

Language in Path
````````````````

* Add ``transurlvania.middleware.LangInPathMiddleware`` to ``MIDDLEWARE_CLASSES``
  after ``LocaleMiddleware``.

* Make these changes to your root URL conf module:

  * If you haven't already done so, replace
    ``from django.conf.urls.defaults import *`` with
    ``from transurlvania.defaults import *``.

  * Replace the call to ``patterns`` that populates the ``urlpatterns``
    variable with a call to ``lang_prefixed_patterns``.

  * To handle requests to the root URL itself ("/") or any URLs you wish to
    keep outside of the language prefixing, declare the URL patterns as
    normal inside a call to ``patterns`` and append the result to the
    ``urlpatterns`` variable.

  Here's an example of what a root URLconf might look like before adding
  language prefixing::

      from django.contrib import admin
      from django.utils.translation import ugettext_noop as _

      from transurlvania.defaults import *

      admin.autodiscover()

      urlpatterns = patterns('example.views',
          url(r'^$', 'home'),
          url(r'^admin/', include(admin.site.urls)),
          url(_(r'^about-us/$'), 'about_us', name='about_us'),
      )

  And here's what it would look like after it's been converted::

      from django.contrib import admin
      from django.utils.translation import ugettext_noop as _

      from transurlvania.defaults import *

      admin.autodiscover()

      urlpatterns = lang_prefixed_patterns('example.views',
          url(r'^$', 'home'),
          url(r'^admin/', include(admin.site.urls)),
          url(_(r'^about-us/$'), 'about_us', name='about_us'),
      )


      urlpatterns += patterns('example.views',
          url(r'^$', 'language_selection_splash'),
          )

Language in Domain
``````````````````

* Add ``transurlvania.middleware.LangInDomainMiddleware`` to ``MIDDLEWARE_CLASSES``
  after ``LocaleMiddleware``.

* Add ``MULTILANG_LANGUAGE_DOMAINS`` to the project's settings module.

  This settings should be a dictionary mapping language codes to two-element
  tuples, where the first element is the domain for that language, and the
  second element is the name of the site this represents.

  Example::

      MULTILANG_LANGUAGE_DOMAINS = {
          'en': ('www.example-en.com', 'English Site'),
          'fr': ('www.example-fr.com', 'French Site')
      }


Language Switching
``````````````````

Django's language switching view is incompatible with transurlvania's
techniques for setting site language using the URL. transurlvania provides its
own language switching tools that make it possible to link directly to the
loaded page's alternate-language equivalent.

The main requirement for this functionality is that
``transurlvania.middleware.URLTransMiddleware`` is in ``MIDDLEWARE_CLASSES``, and
``transurlvania.context_processors.translate`` is in
``TEMPLATE_CONTEXT_PROCESSORS``. With these installed you can then use the
``this_page_in_lang`` template tag to get the URL for the page currently being
viewed in the language requested.

So, ``{% this_page_in_lang "fr" %}`` would return the URL to the French
version of the page being displayed.

The language switching code has two schemes for determining the URL to use:

1. If there's a variable named ``object`` in the context, and that variable
implements a method named ``get_translation``, the switcher will call the
method with the requsted language, call ``get_absolute_url`` on what's
returned and then use that URL for the translation.

2. If the first method fails, the switcher will call transurlvania's
reverse_for_language function using the view name and the parameters that were
resolved from the current request.

There are cases where neither of these schemes will work such as when the
object isn't named ``object``, or when the same view is used by multiple URLs.
In those cases, you can use the decorators provided by the ``translators``
module to decorate the view and change which URL look-up scheme is used. You
can also define your own look-up schemes.

Language Based Blocking
~~~~~~~~~~~~~~~~~~~~~~~

The ``BlockLocaleMiddleware`` will block non-admins from accessing the site in any language
listed in the ``BLOCKED_LANGUAGES`` setting in the settings file.
