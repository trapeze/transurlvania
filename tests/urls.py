from django.conf.urls.defaults import *
from django.contrib import admin
from django.utils.translation import ugettext_noop as _

from multilang.urlresolvers import turl

admin.autodiscover()

urlpatterns = patterns('test_app.views',
    (r'^$', 'home'),
    turl(r'^admin/', include(admin.site.urls)),
    url(r'^non-trans-stuff/$', 'stuff', name='stuff'),
    turl(_(r'^trans-things/$'), 'things'),
    turl(_(r'^multi-module-spangles/'), include('spangles_urls')),
    turl(_(r'^news-story/(?P<slug>[-\w]+)/$'), 'news_story_detail', {}, name='multilang_test_news_detail'),
)
