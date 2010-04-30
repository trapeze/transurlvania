from django.contrib import admin
from django.utils.translation import ugettext_noop as _

from multilang.defaults import *

admin.autodiscover()

urlpatterns = patterns('test_app.views',
    url(r'^$', 'home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^non-trans-stuff/$', 'stuff', name='stuff'),
    url(_(r'^trans-things/$'), 'things'),
    url(_(r'^multi-module-spangles/'), include('spangles_urls')),
    url(_(r'^news-story/(?P<slug>[-\w]+)/$'), 'news_story_detail', {}, name='multilang_test_news_detail'),
)
