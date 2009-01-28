import re

from django.contrib.auth.models import User
from django.core.urlresolvers import get_resolver, reverse
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
        self.assertEqual(reverse(things, 'multilang.tests.urls'), '/trans-things/')
        translation.activate('fr')
        self.assertEqual(reverse(things, 'multilang.tests.urls'), '/trans-chose/')


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
        self.assertTrue(isinstance(ns.core, NewsStoryCore))
