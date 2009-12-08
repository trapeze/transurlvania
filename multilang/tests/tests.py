#encoding=utf8
import re

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_resolver, reverse, clear_url_caches
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase, Client
from django.utils import translation

from multilang import urlresolvers as multilang_resolvers
from multilang.tests import settings as test_settings
from multilang.tests.models import NewsStory, NewsStoryCore
from multilang.tests.views import home, stuff, things, spangles_stars, spangles_stripes
from multilang.tests.views import multilang_home
from multilang.translators import NoTranslationError
from multilang.urlresolvers import reverse_for_language
from multilang.utils import complete_url


class TransURLTestCase(TestCase):
    """
    Test the translatable URL functionality
    These tests require that English (en) and French (fr) are both listed in
    the LANGUAGES list in settings.
    """
    def setUp(self):
        self.resolver = get_resolver('multilang.tests.urls')

    def tearDown(self):
        translation.deactivate()

    def testRootURLIsLangAgnostic(self):
        translation.activate('en')
        self.assertEqual(self.resolver.resolve('/')[0], home)
        translation.activate('fr')
        self.assertEqual(self.resolver.resolve('/')[0], home)

    def testNormalURL(self):
        translation.activate('en')
        self.assertEqual(self.resolver.resolve('/non-trans-stuff/')[0], stuff)
        translation.activate('fr')
        self.assertEqual(self.resolver.resolve('/non-trans-stuff/')[0], stuff)

    def testTransMatches(self):
        translation.activate('en')
        self.assertEqual(self.resolver.resolve('/trans-things/')[0], things)
        translation.activate('fr')
        self.assertEqual(self.resolver.resolve('/trans-chose/')[0], things)

    def testMultiModuleMixedURL(self):
        translation.activate('en')
        self.assertEqual(self.resolver.resolve('/multi-module-spangles/non-trans-stars/')[0], spangles_stars)
        translation.activate('fr')
        self.assertEqual(self.resolver.resolve('/module-multi-de-spangles/non-trans-stars/')[0], spangles_stars)

    def testMultiModuleTransURL(self):
        translation.activate('en')
        self.assertEqual(self.resolver.resolve('/multi-module-spangles/trans-stripes/')[0], spangles_stripes)
        translation.activate('fr')
        self.assertEqual(self.resolver.resolve('/module-multi-de-spangles/trans-bandes/')[0], spangles_stripes)

    def testRootURLReverses(self):
        translation.activate('en')
        self.assertEqual(reverse(home, 'multilang.tests.urls'), '/')
        translation.activate('fr')
        self.assertEqual(reverse(home, 'multilang.tests.urls'), '/')

    def testNormalURLReverses(self):
        translation.activate('en')
        self.assertEqual(reverse(stuff, 'multilang.tests.urls'), '/non-trans-stuff/')
        translation.activate('fr')
        self.assertEqual(reverse(stuff, 'multilang.tests.urls'), '/non-trans-stuff/')

    def testTransReverses(self):
        translation.activate('en')
        self.assertEqual(reverse(spangles_stripes, 'multilang.tests.urls'), '/multi-module-spangles/trans-stripes/')
        # Simulate URLResolver cache reset between requests
        clear_url_caches()
        translation.activate('fr')
        self.assertEqual(reverse(spangles_stripes, 'multilang.tests.urls'), '/module-multi-de-spangles/trans-bandes/')


class ReverseForLanguageTestCase(TestCase):
    """
    Test the `reverse_for_language` functionality.
    These tests require that English (en) and French (fr) are both listed in
    the LANGUAGES list in settings.
    """
    def setUp(self):
        self.resolver = get_resolver('multilang.tests.urls')

    def tearDown(self):
        translation.deactivate()
        test_settings.LANGUAGE_DOMAINS = {}
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

    def testSameDomain(self):
        test_settings.LANGUAGE_DOMAINS = {}
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        translation.activate('en')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            '/multi-module-spangles/trans-stripes/'
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            '/module-multi-de-spangles/trans-bandes/'
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            '/module-multi-de-spangles/trans-bandes/'
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            '/multi-module-spangles/trans-stripes/'
        )

    def testOneDifferentDomain(self):
        test_settings.LANGUAGE_DOMAINS = {
            'fr': ('www.trapeze-fr.com', 'French Site')
        }
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        fr_domain = test_settings.LANGUAGE_DOMAINS['fr'][0]

        translation.activate('en')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            '/multi-module-spangles/trans-stripes/'
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            'http://%s/module-multi-de-spangles/trans-bandes/' % fr_domain
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            'http://%s/module-multi-de-spangles/trans-bandes/' % fr_domain
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            '/multi-module-spangles/trans-stripes/'
        )

    def testBothDifferentDomains(self):
        test_settings.LANGUAGE_DOMAINS = {
            'en': ('www.trapeze.com', 'English Site'),
            'fr': ('www.trapeze-fr.com', 'French Site')
        }
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        en_domain = test_settings.LANGUAGE_DOMAINS['en'][0]
        fr_domain = test_settings.LANGUAGE_DOMAINS['fr'][0]

        translation.activate('en')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            'http://%s/multi-module-spangles/trans-stripes/' % en_domain
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            'http://%s/module-multi-de-spangles/trans-bandes/' % fr_domain
        )

        translation.activate('fr')
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'fr', 'multilang.tests.urls'),
            'http://%s/module-multi-de-spangles/trans-bandes/' % fr_domain
        )
        self.assertEquals(
            reverse_for_language(spangles_stripes, 'en', 'multilang.tests.urls'),
            'http://%s/multi-module-spangles/trans-stripes/' % en_domain
        )


class LangInPathTestCase(TestCase):
    """
    Test language setting via URL path
    LocaleMiddleware and LangInPathMiddleware must be listed in
    MIDDLEWARE_CLASSES for these tests to run properly.
    """
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        translation.deactivate()

    def testRootURLIsLangAgnostic(self):
        self.client.cookies['django_language'] = 'de'
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multilang_tests/multilang_home.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'de')

    def testNormalURL(self):
        response = self.client.get('/en/non-trans-stuff/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multilang_tests/stuff.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'en')
        response = self.client.get('/fr/non-trans-stuff/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multilang_tests/stuff.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'fr')

    def testTranslatedURL(self):
        response = self.client.get('/en/trans-things/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multilang_tests/things.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'en')
        response = self.client.get('/fr/trans-chose/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'multilang_tests/things.html')
        self.assertEqual(response.context.get('LANGUAGE_CODE', None), 'fr')


class LangInDomainTestCase(TestCase):
    """
    Test language setting via URL path
    LangInDomainMiddleware must be listed in MIDDLEWARE_CLASSES for these tests
    to run properly.
    """
    def tearDown(self):
        translation.deactivate()

    def testRootURL(self):
        translation.activate('en')
        client = Client(SERVER_NAME='www.trapeze-fr.com')
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'fr')

        translation.activate('fr')
        self.client = Client(SERVER_NAME='www.trapeze-en.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'en')

    def testURLWithPrefixes(self):
        translation.activate('en')
        client = Client(SERVER_NAME='www.trapeze-fr.com')
        response = client.get('/en/non-trans-stuff/')
        self.assertEqual(response.status_code, 404)
        response = client.get('/fr/non-trans-stuff/')
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'fr')

        translation.activate('fr')
        client = Client(SERVER_NAME='www.trapeze-en.com')
        response = client.get('/fr/non-trans-stuff/')
        self.assertEqual(response.status_code, 404)
        response = client.get('/en/non-trans-stuff/')
        self.assertEqual(response.context.get('LANGUAGE_CODE'), 'en')


class LanguageSwitchingTestCase(TestCase):
    fixtures = ['test.json']
    """
    Test the language switching functionality of multilang (which also tests
    the `this_page_in_lang` template tag).
    """
    def setUp(self):
        self.client = Client()
        self.french_version_anchor_re = re.compile(r'<a class="french-version-link" href="([^"]*)">')

    def tearDown(self):
        translation.deactivate()
        test_settings.LANGUAGE_DOMAINS = {}
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

    def testDefaultViewBasedSwitching(self):
        response = self.client.get('/en/trans-things/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url, '/fr/trans-chose/')

    def testDefaultObjectBasedSwitching(self):
        test_settings.LANGUAGE_DOMAINS = {}
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        response = self.client.get('/en/news-story/english-test-story/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url, '/fr/nouvelle/histoire-du-test-francais/')

    def testDefaultViewBasedSwitchingWithSeparateDomains(self):
        test_settings.LANGUAGE_DOMAINS = {
            'fr': ('www.trapeze-fr.com', 'French Site')
        }
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        response = self.client.get('/en/trans-things/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url,
            'http://www.trapeze-fr.com/fr/trans-chose/'
        )

    def testDefaultObjectBasedSwitchingWithSeparateDomains(self):
        test_settings.LANGUAGE_DOMAINS = {
            'fr': ('www.trapeze-fr.com', 'French Site')
        }
        multilang_resolvers.LANGUAGE_DOMAINS = test_settings.LANGUAGE_DOMAINS

        response = self.client.get('/en/news-story/english-test-story/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url,
            'http://www.trapeze-fr.com/fr/nouvelle/histoire-du-test-francais/'
        )
        
    def testThisPageInLangTagWithFallBack(self):
        
        template = Template('{% load multilang_tags %}'
            '{% this_page_in_lang "fr" "/en/home/" %}'
        )
        output = template.render(Context({}))
        self.assertEquals(output, "/en/home/")
        
    def testThisPageInLangTagWithVariableFallBack(self):
        translation.activate('en')
        template = Template('{% load multilang_tags %}'
            '{% url stuff as myurl %}'
            '{% this_page_in_lang "fr" myurl %}'
        )
        output = template.render(Context({}))
        self.assertEquals(output, '/en/non-trans-stuff/')
    
    def testThisPageInLangTagNoArgs(self):
        try:
            template = Template('{% load multilang_tags %}'
                '{% this_page_in_lang %}'
            )
        except TemplateSyntaxError, e:
            self.assertEquals(e.message, 'this_page_in_lang tag requires at least one argument')
        else:
            self.fail()
    
    def testThisPageInLangTagExtraArgs(self):
        try:
            template = Template('{% load multilang_tags %}'
                '{% this_page_in_lang "fr" "/home/" "/sadf/" %}'
            )
        except TemplateSyntaxError, e:
            self.assertEquals(e.message, 'this_page_in_lang tag takes at most two arguments')
        else:
            self.fail()
        

class MultiLangAdminTestCase(TestCase):
    """
    Test MultiLangAdmin pages to make sure they exist
    """
    def setUp(self):
        User.objects.create_superuser("admin", "admin@test.com", "admin")
        self.client = Client()
        self.client.login(username="admin", password="admin")

    def testCoreAdminChangeListURL(self):
        response = self.client.get('/admin/tests/newsstorycore/')
        self.assertEqual(response.status_code, 200)

    def testTransAdminChangeListURL(self):
        response = self.client.get('/admin/tests/newsstory/')
        self.assertEqual(response.status_code, 200)

    def testCoreAdminAddViewURL(self):
        response = self.client.get('/admin/tests/newsstorycore/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/ml_change_form.html')

    def testTransAdminAddViewURL(self):
        response = self.client.get('/admin/tests/newsstory/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/ml_change_form.html')

    def testCoreAdminChangeViewURL(self):
        n = NewsStoryCore()
        n.save()
        response = self.client.get('/admin/tests/newsstorycore/%s/' % n.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/ml_change_form.html')

    def testTransAdminChangeViewURL(self):
        n = NewsStoryCore()
        n.save()
        s = NewsStory(language="en", core=n, headline="test", slug="test", body="test")
        s.save()
        response = self.client.get('/admin/tests/newsstory/%s/' % s.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/ml_change_form.html')


class CoreAutosaveTestCase(TestCase):
    def testCoreCreated(self):
        ns = NewsStory(language='en', headline='test', slug='test', body='test')
        ns.save()
        self.assertTrue(isinstance(ns.core, NewsStoryCore))
        ns1 = NewsStory.objects.get(pk=ns.pk)
        self.assertTrue(isinstance(ns1.core, NewsStoryCore))


class TransInLangTagTestCase(TestCase):
    """Tests for the `trans_in_lang` template tag."""

    def tearDown(self):
        translation.deactivate()

    def testBasic(self):
        """
        Tests the basic usage of the tag.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"fr" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

        translation.activate('fr')
        template_content = '{% load multilang_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French')

    def testVariableArgument(self):
        """
        Tests the tag when using a variable as the lang argument.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% with "French" as myvar %}{% with "fr" as lang %}{{ myvar|trans_in_lang:lang }}{% endwith %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

    def testKeepsPresetLanguage(self):
        """
        Tests that the tag does not change the language.
        """
        translation.activate('en')
        template_content = '{% load i18n %}{% load multilang_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"fr" }}|{% trans "French" %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français|French')

        translation.activate('fr')
        template_content = '{% load i18n %}{% load multilang_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}|{% trans "French" %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français')

    def testNoTranslation(self):
        """
        Tests the tag when there is no translation for the given string.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% with "somethinginvalid" as myvar %}{{ myvar|trans_in_lang:"fr" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'somethinginvalid')

    def testRepeated(self):
        """
        Tests the tag when it is used repeatedly for different languages.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% with "French" as myvar %}{{ myvar|trans_in_lang:"en" }}|{{ myvar|trans_in_lang:"fr" }}|{{ myvar|trans_in_lang:"de" }}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français|Französisch')


class MultilangModelTestCase(TestCase):
    """
    Test the internal translatable model functionality
    """
    fixtures = ['test.json']

    def testTranslationIsProvidedWhenAvailable(self):
        # Get English news story core that has English and French translations
        ns_core = NewsStoryCore.objects.get(pk=1)
        ns_en = ns_core.translations.get(language='en')
        ns_fr = ns_core.translations.get(language='fr')

        self.assertEqual(ns_en.get_translation('fr'), ns_fr)

    def testRaisesErrorWhenTranslationUnavailable(self):
        # Get English news story core that only has an English translation
        ns_core = NewsStoryCore.objects.get(pk=2)
        ns_en = ns_core.translations.get(language='en')

        self.assertRaises(NoTranslationError, ns_en.get_translation, 'fr')


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
