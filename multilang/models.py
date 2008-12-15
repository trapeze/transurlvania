from django.db import models
from django.utils.translation import ugettext_lazy as _

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
