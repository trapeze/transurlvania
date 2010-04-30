from django.utils.translation import ugettext_noop as _

from multilang.defaults import *


urlpatterns = patterns('test_app.views',
    (r'^$', 'spangles_home'),
    (r'^non-trans-stars/$', 'spangles_stars'),
    url(_(r'^trans-stripes/'), 'spangles_stripes'),
)
