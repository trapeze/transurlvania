from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.utils.translation import ugettext_noop as _

from multilang.urlresolvers import turl


admin.autodiscover()


urlpatterns = patterns('',
    # Language Prefixed URLs
    turl(_(r'^LANG_CODE/'), include('multilang.tests.urls')),

    # Home / Landing
    (r'^$', 'multilang.tests.views.multilang_home'),

    # Admin
    url(r'^admin/(.*)', admin.site.root, name="admin"),
)
