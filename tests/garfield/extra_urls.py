from django.utils.translation import ugettext_noop as _

from transurlvania.defaults import *


urlpatterns = patterns('garfield.views',
    url(r'^jim-davis/$', 'jim_davis', name='garfield_jim_davis'),
)
