from django.conf import settings
from django.utils.translation import ugettext_noop as _

from multilang.defaults import *
from multilang.urlresolvers import turl, lang_prefixed


admin.autodiscover()


urlpatterns = patterns('',
    # Language Prefixed URLs
    lang_prefixed('tests.urls'),

    # Home / Landing
    (r'^$', 'test_app.views.multilang_home'),
)
