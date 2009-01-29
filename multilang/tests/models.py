import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from multilang.decorators import multilang_permalink
from multilang.models import LangAgnostic, LangTranslatable


class NewsStoryCore(LangAgnostic):
    """
    The core, language-agnostic part of a news story
    """
    publication_date = models.DateTimeField(_('publish date/time'),
        default=datetime.datetime.now)
    public = models.BooleanField(_('public'), default=True)

    class Meta:
        verbose_name = _('news story')
        verbose_name_plural = _('news stories')

    def __unicode__(self):
        if self.headline:
            return u"News Story: %s" % self.headline
        else:
            return u"News Story"

    @property
    def headline(self):
        return self.get_trans_field('headline')


class NewsStory(LangTranslatable):
    """
    A news story that can be translated into multiple languages
    """
#TODO: why are we using null=True?
    core = models.ForeignKey(NewsStoryCore, null=True, blank=True,
        verbose_name=_('core news story'), related_name='translations')
    headline = models.CharField(_('headline'), max_length=255)
    slug = models.SlugField(_('slug'))
    body = models.TextField(_('body'))

    class Meta:
        verbose_name = _('news story translation')
        verbose_name_plural = _('news story translations')
        unique_together = ('core', 'language')

    def __unicode__(self):
        return self.headline

    @multilang_permalink
    def get_absolute_url(self):
        return ('multilang_test_news_detail', self.language, (), {
            'slug': self.slug,
        })
