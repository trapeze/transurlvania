#encoding=utf-8
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_resolver, reverse, clear_url_caches
from django.core.urlresolvers import NoReverseMatch
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase, Client
from django.utils import translation, http

import transurlvania.settings
from transurlvania import urlresolvers as transurlvania_resolvers
from transurlvania.translators import NoTranslationError
from transurlvania.urlresolvers import reverse_for_language
from transurlvania.utils import complete_url
from transurlvania.views import detect_language_and_redirect

from garfield.views import home, about_us, the_president
from garfield.views import comic_strip_list, comic_strip_detail, landing
from garfield.views import jim_davis


french_version_anchor_re = re.compile(r'<a class="french-version-link" href="([^"]*)">')


class TransURLTestCase(TestCase):
    """
    Test the translatable URL functionality
    These tests require that English (en) and French (fr) are both listed in
    the LANGUAGES list in settings.
    """
    def setUp(self):
        translation.activate('en')

    def tearDown(self):
        translation.deactivate()
        clear_url_caches()

    def testNormalURL(self):
        self.assertEqual(get_resolver(None).resolve('/en/garfield/')[0], landing)
        translation.activate('fr')
        self.assertEqual(get_resolver(None).resolve('/fr/garfield/')[0], landing)

    def testTransMatches(self):
        self.assertEqual(get_resolver(None).resolve('/en/about-us/')[0], about_us)
        translation.activate('fr')
        self.assertEqual(get_resolver(None).resolve('/fr/a-propos-de-nous/')[0], about_us)

    def testMultiModuleMixedURL(self):
        self.assertEqual(get_resolver(None).resolve('/en/garfield/jim-davis/')[0], jim_davis)
        translation.activate('fr')
        self.assertEqual(get_resolver(None).resolve('/fr/garfield/jim-davis/')[0], jim_davis)

    def testMultiModuleTransURL(self):
        self.assertEqual(get_resolver(None).resolve(u'/en/garfield/the-president/')[0], the_president)
        translation.activate('fr')
        self.assertEqual(get_resolver(None).resolve(u'/fr/garfield/le-président/')[0], the_president)

    def testRootURLReverses(self):
        self.assertEqual(reverse(detect_language_and_redirect, 'tests.urls'), '/')
        translation.activate('fr')
        self.assertEqual(reverse(detect_language_and_redirect, 'tests.urls'), '/')

    def testNormalURLReverses(self):
        translation.activate('en')
        self.assertEqual(reverse(landing), '/en/garfield/')
        clear_url_caches()
        translation.activate('fr')
        self.assertEqual(reverse(landing), '/fr/garfield/')

    def testTransReverses(self):
        translation.activate('en')
        self.assertEqual(reverse(the_president), '/en/garfield/the-president/')
        # Simulate URLResolver cache reset between requests
        clear_url_caches()
        translation.activate('fr')
        self.assertEqual(reverse(the_president), http.urlquote(u'/fr/garfield/le-président/'))

    def testReverseForLangSupportsAdmin(self):
        try:
            reverse_for_language('admin:garfield_comicstrip_add', 'en')
        except NoReverseMatch, e:
            self.fail("Reverse lookup failed: %s" % e)


class LangInPathTestCase(TestCase):
    """
    Test language setting via URL path
    LocaleMiddleware and LangInPathMiddleware must be listed in
    MIDDLEWARE_CLASSES for these tests to run properly.
    """
    def setUp(self):
        translation.activate('en')

    def tearDown(self):
        translation.deactivate()

    def testLangDetectionViewRedirectsToLang(self):
        self.client.cookies['django_language'] = 'de'
        response = self.client.get('/')
        self.assertRedirects(response, '/de/')

    def testNormalURL(self):
        response = self.client.get('/en/garfield/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garfield/landing.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'en')
        response = self.client.get('/fr/garfield/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garfield/landing.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'fr')

    def testTranslatedURL(self):
        response = self.client.get('/en/garfield/the-cat/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garfield/comicstrip_list.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'en')
        response = self.client.get('/fr/garfield/le-chat/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garfield/comicstrip_list.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'fr')

    def testReverseForLanguage(self):
        translation.activate('en')
        self.assertEquals(
            reverse_for_language(the_president, 'en'),
            '/en/garfield/the-president/'
        )
        self.assertEquals(
            reverse_for_language(the_president, 'fr'),
            http.urlquote('/fr/garfield/le-président/')
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(the_president, 'fr'),
            http.urlquote('/fr/garfield/le-président/')
        )
        self.assertEquals(
            reverse_for_language(the_president, 'en'),
            '/en/garfield/the-president/'
        )


class LangInDomainTestCase(TestCase):
    """
    Test language setting via URL path
    LangInDomainMiddleware must be listed in MIDDLEWARE_CLASSES for these tests
    to run properly.
    """
    urls = 'tests.urls_without_lang_prefix'

    def setUp(self):
        transurlvania.settings.LANGUAGE_DOMAINS = {
            'en': ('www.trapeze-en.com', 'English Site'),
            'fr': ('www.trapeze-fr.com', 'French Site')
        }

    def tearDown(self):
        translation.deactivate()
        transurlvania.settings.LANGUAGE_DOMAINS = {}

    def testRootURL(self):
        translation.activate('en')
        client = Client(SERVER_NAME='www.trapeze-fr.com')
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'fr')
        transurlvania.settings.LANGUAGE_DOMAINS = {}

        translation.activate('fr')
        self.client = Client(SERVER_NAME='www.trapeze-en.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'en')

    def testURLWithPrefixes(self):
        translation.activate('en')
        response = self.client.get('/en/garfield/', SERVER_NAME='www.trapeze-fr.com')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/fr/garfield/', SERVER_NAME='www.trapeze-fr.com')
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'fr')

        translation.activate('fr')
        client = Client(SERVER_NAME='www.trapeze-en.com')
        response = client.get('/fr/garfield/')
        self.assertEqual(response.status_code, 404)
        response = client.get('/en/garfield/')
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'en')

    def testReverseForLangWithOneDifferentDomain(self):
        transurlvania.settings.LANGUAGE_DOMAINS = {
            'fr': ('www.trapeze-fr.com', 'French Site')
        }

        fr_domain = transurlvania.settings.LANGUAGE_DOMAINS['fr'][0]

        translation.activate('en')
        self.assertEquals(reverse_for_language(about_us, 'en'), '/about-us/')
        self.assertEquals(
            reverse_for_language(about_us, 'fr'),
            u'http://%s/a-propos-de-nous/' % fr_domain
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(about_us, 'fr'),
            u'http://%s/a-propos-de-nous/' % fr_domain
        )
        self.assertEquals(
            reverse_for_language(about_us, 'en'),
            '/about-us/'
        )

    def testBothDifferentDomains(self):
        transurlvania.settings.LANGUAGE_DOMAINS = {
            'en': ('www.trapeze.com', 'English Site'),
            'fr': ('www.trapeze-fr.com', 'French Site')
        }

        en_domain = transurlvania.settings.LANGUAGE_DOMAINS['en'][0]
        fr_domain = transurlvania.settings.LANGUAGE_DOMAINS['fr'][0]

        translation.activate('en')
        self.assertEquals(
            reverse_for_language(about_us, 'en', 'tests.urls'),
            'http://%s/en/about-us/' % en_domain
        )
        self.assertEquals(
            reverse_for_language(about_us, 'fr', 'tests.urls'),
            'http://%s/fr/a-propos-de-nous/' % fr_domain
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(about_us, 'fr', 'tests.urls'),
            'http://%s/fr/a-propos-de-nous/' % fr_domain
        )
        self.assertEquals(
            reverse_for_language(about_us, 'en', 'tests.urls'),
            'http://%s/en/about-us/' % en_domain
        )

    def testDefaultViewBasedSwitchingWithSeparateDomains(self):
        transurlvania.settings.LANGUAGE_DOMAINS = {
            'fr': ('www.trapeze-fr.com', 'French Site')
        }

        response = self.client.get('/about-us/')
        french_version_url = french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url,
            'http://www.trapeze-fr.com/a-propos-de-nous/'
        )



class LanguageSwitchingTestCase(TestCase):
    fixtures = ['test.json']
    """
    Test the language switching functionality of transurlvania (which also tests
    the `this_page_in_lang` template tag).
    """
    def tearDown(self):
        translation.deactivate()

    def testDefaultViewBasedSwitching(self):
        response = self.client.get('/en/about-us/')
        self.assertTemplateUsed(response, 'about_us.html')
        french_version_url = french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url, '/fr/a-propos-de-nous/')

    def testThisPageInLangTagWithFallBack(self):

        template = Template('{% load transurlvania_tags %}'
            '{% this_page_in_lang "fr" "/en/home/" %}'
        )
        output = template.render(Context({}))
        self.assertEquals(output, "/en/home/")

    def testThisPageInLangTagWithVariableFallBack(self):
        translation.activate('en')
        template = Template('{% load transurlvania_tags %}'
            '{% url garfield_landing as myurl %}'
            '{% this_page_in_lang "fr" myurl %}'
        )
        output = template.render(Context({}))
        self.assertEquals(output, '/en/garfield/')

    def testThisPageInLangTagNoArgs(self):
        try:
            template = Template('{% load transurlvania_tags %}'
                '{% this_page_in_lang %}'
            )
        except TemplateSyntaxError, e:
            self.assertEquals(unicode(e), u'this_page_in_lang tag requires at least one argument')
        else:
            self.fail()

    def testThisPageInLangTagExtraArgs(self):
        try:
            template = Template('{% load transurlvania_tags %}'
                '{% this_page_in_lang "fr" "/home/" "/sadf/" %}'
            )
        except TemplateSyntaxError, e:
            self.assertEquals(unicode(e), u'this_page_in_lang tag takes at most two arguments')
        else:
            self.fail()

# TODO: Add tests for views that implement the view-based and object-based
# translation schemes.


class TransInLangTagTestCase(TestCase):
    """Tests for the `trans_in_lang` template tag."""

    def tearDown(self):
        translation.deactivate()

    def testBasic(self):
        """
        Tests the basic usage of the tag.
        """
        translation.activate('en')
        template_content = '{% load transurlvania_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"fr" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

        translation.activate('fr')
        template_content = '{% load transurlvania_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French')

    def testVariableArgument(self):
        """
        Tests the tag when using a variable as the lang argument.
        """
        translation.activate('en')
        template_content = '{% load transurlvania_tags %}{% with "French" as myvar %}{% with "fr" as lang %}{{ myvar|trans_in_lang:lang }}{% endwith %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

    def testKeepsPresetLanguage(self):
        """
        Tests that the tag does not change the language.
        """
        translation.activate('en')
        template_content = '{% load i18n %}{% load transurlvania_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"fr" }}|{% trans "French" %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français|French')

        translation.activate('fr')
        template_content = '{% load i18n %}{% load transurlvania_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}|{% trans "French" %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français')

    def testNoTranslation(self):
        """
        Tests the tag when there is no translation for the given string.
        """
        translation.activate('en')
        template_content = '{% load transurlvania_tags %}{% with "somethinginvalid" as myvar %}{{ myvar|trans_in_lang:"fr" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'somethinginvalid')

    def testRepeated(self):
        """
        Tests the tag when it is used repeatedly for different languages.
        """
        translation.activate('en')
        template_content = '{% load transurlvania_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}|{{ myvar|trans_in_lang:"fr" }}|{{ myvar|trans_in_lang:"de" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français|Französisch')


def CompleteURLTestCase(TestCase):
    """
    Tests the `complete_url` utility function.
    """
    def tearDown(self):
        translation.deactivate()

    def testPath(self):
        translation.activate('en')
        self.assertEquals(complete_url('/path/'),
            'http://www.trapeze-en.com/path/'
        )
        translation.activate('fr')
        self.assertEquals(complete_url('/path/'),
            'http://www.trapeze-fr.com/path/'
        )

    def testFullUrl(self):
        translation.activate('fr')
        self.assertEquals(complete_url('http://www.google.com/path/'),
            'http://www.google.com/path/'
        )

    def testNoDomain(self):
        translation.activate('de')
        self.assertRaises(ImproperlyConfigured, complete_url, '/path/')

    def testExplicitLang(self):
        translation.activate('en')
        self.assertEquals(complete_url('/path/', 'fr'),
            'http://www.trapeze-fr.com/path/'
        )
        translation.activate('en')
        self.assertEquals(complete_url('/path/', 'en'),
            'http://www.trapeze-en.com/path/'
        )
