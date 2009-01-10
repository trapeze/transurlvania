from django.conf.urls.defaults import *
from django.utils.translation import ugettext_noop as _

from multilang.urlresolvers import turl

urlpatterns = patterns('multilang.tests.views',
    (r'^$', 'home'),
    (r'^non-trans-stuff/$', 'stuff'),
    turl(_(r'^trans-things/$'), 'things'),
    turl(_(r'^multi-module-spangles/'), include('multilang.tests.spangles_urls')),
    )
