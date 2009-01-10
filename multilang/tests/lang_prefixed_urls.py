from django.conf import settings
from django.conf.urls.defaults import *
from django.utils.translation import ugettext_noop as _

from multilang.urlresolvers import turl

urlpatterns = patterns('',
    turl(_(r'^LANG_CODE/'), include('multilang.tests.urls')),
    (r'^$', 'multilang.tests.views.multilang_home'),
    )
