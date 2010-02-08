from django.conf.urls.defaults import *
from django.utils.translation import ugettext_noop as _

from multilang.urlresolvers import turl


urlpatterns = patterns('test_app.views',
    (r'^$', 'spangles_home'),
    (r'^non-trans-stars/$', 'spangles_stars'),
    turl(_(r'^trans-stripes/'), 'spangles_stripes'),
)
