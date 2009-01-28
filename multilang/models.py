from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _

from multilang.choices import LANGUAGES_CHOICES


class LangSpecific(models.Model):
    """
    An abstract model that provides the language field
    """
    language = models.CharField(_('language'), max_length=5, choices=LANGUAGES_CHOICES)

    class Meta:
        abstract = True


class LangManager(models.Manager):
    def get_query_set(self):
        # TODO: Confirm that this is needed
        return super(LangManager, self).get_query_set().select_related(depth=1)


class LangAgnostic(models.Model):
    """
    The language agnostic half of the two-model multilang pair
    """
    class Meta:
        abstract = True

    def __unicode__(self):
        trans_str_list = [u'%s (%s)' % (obj, obj.get_language_display()) for obj in self.translations.all()]
        return u'(%s)' % u', '.join(trans_str_list)

    def get_trans_field(self, field):
        try:
            trans_obj = self.translations.get(language=get_language())
        except self.translations.model.DoesNotExist:
            try:
                trans_obj = self.translations.all()[0]
            except IndexError:
                return None

        return getattr(trans_obj, field)


class LangTranslatable(LangSpecific):
    """
    The language dependent half of the two-model multilang pair
    """
    objects = LangManager()

    class Meta:
        abstract = True

    def save(self):
        """
        If the core fk isn't set, attempts to create and save a new object for it.
        """
        try:
            if self.core_id is None:
                core_obj = self._meta.get_field_by_name('core')[0].rel.to()
                core_obj.save()

                self.core = core_obj
        except AttributeError:
            raise ImproperlyConfigured(_('save expects subclasses of '
                    'LangTranslatable to have a "core" ForeignKey field that '
                    'points to an object that instantiates some subclass of '
                    'LangAgnostic.'))
        # TODO: Catch validation errors that result from saving a model entry without
        # providing data for a required field.

        super(LangTranslatable, self).save()

    def get_translation(self, lang):
        try:
            return self.core.translations.get(language=lang)
        except AttributeError:
            raise ImproperlyConfigured('get_translation expects subclasses of '
                                 'LangTranslatable to have a "core" field that '
                                 'points to the LangAgnostic object, with a '
                                 'related_name of "translations".')
        except self.DoesNotExist:
            return self
