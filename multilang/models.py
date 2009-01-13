from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _

from multilang.choices import LANGUAGES_CHOICES


class Translatable(models.Model):
    """An abstract model that provides the framework for making a model translatable"""
    language = models.CharField(_('language'), max_length=5, choices=LANGUAGES_CHOICES)
    translation_of = models.ForeignKey('self', null=True, blank=True,
                        verbose_name=_('translation of'),
                        limit_choices_to={'translation_of__isnull': True})

    class Meta:
        verbose_name = _('translatable')
        verbose_name_plural = _('translatables')
        abstract = True

    def get_translation(self, language_code):
        """Returns the translation of the current object in the language requested,
        or returns the current object if a translation in that language doesn't
        exist.
        """
        if self.language == language_code:
            return self
        try:
            if self.translation_of != None:
                if self.translation_of.language == language_code:
                    return self.translation_of
                else:
                        return self.translation_of.translations.exclude(pk=self.pk).get(language=language_code)
            else:
                return self.translations.get(language=language_code)
        except self.DoesNotExist:
            return self


class LangManager(models.Manager):
    def get_query_set(self):
        # TODO: Confirm that this is needed
        return super(LangManager, self).get_query_set().select_related(depth=1)


class LangAgnostic(models.Model):
    """The language agnostic half of the two-model multilang pair"""
    class Meta:
        abstract = True

    def __unicode__(self):
        trans_str_list = [u'%s (%s)' % (obj, obj.get_language_display()) for obj in self.translations.all()]
        return u'(%s)' % u', '.join(trans_str_list)

    def get_trans_field(self, field):
        try:
            trans_obj = self.translations.get(language=get_language())
        except self.DoesNotExist:
            try:
                trans_obj = self.translations.all()[0]
            except IndexError:
                return None
        return getattr(trans_obj, field)



class LangDependent(models.Model):
    """The language dependent half of the two-model multilang pair"""
    language = models.CharField(_('language'), blank=True, max_length=5, choices=LANGUAGES_CHOICES)

    objects = LangManager()

    class Meta:
        abstract = True

    def get_translation(self, lang):
        try:
            return self.core.translations.get(language=lang)
        except AttributeError:
            raise ImproperlyConfigured('get_translation expects subclasses of '
                                 'LangDependent to have a "core" field that '
                                 'points to the LangAgnostic object, with a '
                                 'related_name of "translations".')
        except self.DoesNotExist:
            return self
