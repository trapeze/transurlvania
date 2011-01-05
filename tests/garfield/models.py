import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from transurlvania.decorators import permalink_in_lang


class ComicStrip(models.Model):
    """
    A Garfield comic strip
    """
    name = models.CharField(_('name'), max_length=255)
    comic = models.URLField(_('comic'))
    publication_date = models.DateTimeField(_('publish date/time'),
        default=datetime.datetime.now)
    public = models.BooleanField(_('public'), default=True)
    language = models.CharField(_('language'), max_length=5,
            choices=settings.LANGUAGES)

    class Meta:
        verbose_name = _('comic strip')
        verbose_name_plural = _('comic strips')

    def __unicode__(self):
        return self.name

    @permalink_in_lang
    def get_absolute_url(self):
        return ('garfield_comic_strip_detail', self.language, (), {'slug': self.slug,})
