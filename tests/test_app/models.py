import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from multilang.decorators import multilang_permalink


class NewsStory(models.Model):
    """
    A news story that can be translated into multiple languages
    """
    headline = models.CharField(_('headline'), max_length=255)
    slug = models.SlugField(_('slug'))
    body = models.TextField(_('body'))
    publication_date = models.DateTimeField(_('publish date/time'),
        default=datetime.datetime.now)
    public = models.BooleanField(_('public'), default=True)
    language = models.CharField(_('language'), max_length=255,
            choices=settings.LANGUAGES)

    class Meta:
        verbose_name = _('news story')
        verbose_name_plural = _('news stories')

    def __unicode__(self):
        return self.headline

    @multilang_permalink
    def get_absolute_url(self):
        return ('multilang_test_news_detail', self.language, (), {
            'slug': self.slug,
        })
