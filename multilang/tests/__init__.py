from django.core.urlresolvers import get_resolver
from django.test import TestCase, Client
from django.utils import translation

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
