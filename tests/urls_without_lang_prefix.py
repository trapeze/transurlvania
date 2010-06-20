from django.contrib import admin
from django.utils.translation import ugettext_noop as _

from transurlvania.defaults import *

admin.autodiscover()

urlpatterns = patterns('garfield.views',
    url(r'^$', 'home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^garfield/', include('garfield.urls')),
    url(_(r'^about-us/$'), 'about_us', name='about_us'),
)
