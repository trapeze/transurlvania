#encoding=utf8
import re

from django.contrib.auth.models import User
from django.core.urlresolvers import get_resolver, reverse, clear_url_caches
from django.template import Context, Template
from django.test import TestCase, Client
from django.utils import translation

from multilang.tests.models import NewsStory, NewsStoryCore
from multilang.tests.views import home, stuff, things, spangles_stars, spangles_stripes
from multilang.tests.views import multilang_home


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


class LangInURLTestCase(TestCase):
    """
    Test language setting via URL path
    LocaleMiddleware and LangInURLMiddleware must be listed in MIDDLEWARE_CLASSES
    for these tests to run properly.
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


class LanguageSwitchingTestCase(TestCase):
    fixtures = ['test.json']
    """
    Test the language switching functionality of multilang.
    """
    def setUp(self):
        self.client = Client()
        self.french_version_anchor_re = re.compile(r'<a class="french-version-link" href="([^"]*)">')

    def testDefaultViewBasedSwitching(self):
        response = self.client.get('/en/trans-things/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url, '/fr/trans-chose/')

    def testDefaultObjectBasedSwitching(self):
        response = self.client.get('/en/news-story/english-test-story/')
        french_version_url = self.french_version_anchor_re.search(response.content).group(1)
        self.assertEqual(french_version_url, '/fr/nouvelle/histoire-du-test-francais/')


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

    def testBasic(self):
        """
        Tests the basic usage of the tag.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% trans_in_lang "French" "fr" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

        translation.activate('fr')
        template_content = '{% load multilang_tags %}{% trans_in_lang "French" "en" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French')

    def testAsKeyword(self):
        """
        Tests the tag when using the `as` keyword.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% trans_in_lang "French" "fr" as myvar %}{{ myvar }}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

    def testVariableArguments(self):
        """
        Tests the tag when using a variables as the arguments.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% with "French" as myvar %}{% with "fr" as lang %}{% trans_in_lang myvar lang %}{% endwith %}{% endwith %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français')

    def testKeepsPresetLanguage(self):
        """
        Tests that the tag does not change the language.
        """
        translation.activate('en')
        template_content = '{% load i18n %}{% load multilang_tags %}{% trans_in_lang "French" "fr" %}|{% trans "French" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'Français|French')

        translation.activate('fr')
        template_content = '{% load i18n %}{% load multilang_tags %}{% trans_in_lang "French" "en" %}|{% trans "French" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français')

    def testNoTranslation(self):
        """
        Tests the tag when there is no translation for the given string.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% trans_in_lang "somethinginvalid" "fr" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'somethinginvalid')

    def testRepeated(self):
        """
        Tests the tag when it is used repeatedly for different languages.
        """
        translation.activate('en')
        template_content = '{% load multilang_tags %}{% trans_in_lang "French" "en" %}|{% trans_in_lang "French" "fr" %}|{% trans_in_lang "French" "de" %}'
        template = Template(template_content)
        output = template.render(Context())
        self.assertEquals(output, u'French|Français|Französisch')
