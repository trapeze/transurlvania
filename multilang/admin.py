from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import FieldDoesNotExist
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _


class MultiLangModelAdmin(admin.ModelAdmin):
    """
    A wrapper around ModelAdmin that allows translatable models to be linked
    to from the change view and vice versa.
    
    It uses the custom variables `ml_relation_name` and `ml_field_name` to 
    introspect the given models, these can be overridden with different
    values if the models are using other names.
    
    Subclass `LangDependentModelAdmin` or `LangAgnosticModelAdmin` when 
    building admin classes, `MultiLangModelAdmin` is used as a shared base 
    class only - it should not be subclassed directly.
    """
    change_form_template = "admin/ml_change_form.html"

    ml_relation_name = "translations"
    ml_field_name = "core"
    ml_trans_model = None
    ml_core_model = None


    def _construct_core_url(self, obj):
        return "../../../%(app)s/%(model)s/%(id)s/" % {
            "app": obj.__class__._meta.app_label,
            "model": obj.__class__.__name__.lower(),
            "id": obj._get_pk_val(),
        }


    def _construct_trans_url(self, lang, obj):
        try:
            trans_obj = self.ml_trans_model._default_manager.get(language=lang, core=obj)
        except self.ml_trans_model.DoesNotExist:
            trans_obj = None
        
        if trans_obj:
            return ("../../../%(app)s/%(model)s/%(id)s/" % {
                "app": self.ml_trans_model._meta.app_label,
                "model": self.ml_trans_model.__name__.lower(),
                "id": trans_obj._get_pk_val(),
            }, True)
        else:
            return ("../../../%(app)s/%(model)s/add/?language=%(lang)s&core=%(id)s" % {
                "app": self.ml_trans_model._meta.app_label,
                "model": self.ml_trans_model.__name__.lower(),
                "lang": lang,
                "id": obj._get_pk_val(),
            }, False)


    def _construct_trans_links(self, obj):
        trans_links = []
        
        trans_links.append({
            "name": obj,
            "url": self._construct_core_url(obj),
            "active": True,
        })
        
        for lang in dict(settings.LANGUAGES):
            url = self._construct_trans_url(lang, obj)
            
            trans_links.append({
                "name": dict(settings.LANGUAGES)[lang],
                "url": url[0],
                "active": url[1],
            })
        
        return trans_links


    class Media:
        css = {
            "all": ("multilang/css/admin.css",),
        }


class LangDependentModelAdmin(MultiLangModelAdmin):
    """
    A subclass of `MultiLangModelAdmin` that should be used for models that 
    have translatable fields and that link to a core model.
    """
    def __init__(self, model, admin_site):
        super(LangDependentModelAdmin, self).__init__(model, admin_site)
        
        try:
            field = model._meta.get_field_by_name(self.ml_field_name)
            
            self.ml_trans_model = model
            self.ml_core_model = field[0].rel.to
        except FieldDoesNotExist:
            raise ImproperlyConfigured("Field %(field)s could not be found in the model %(model)s." % {
                "field": self.ml_field_name,
                "model": model.__name__,
            })
        except AttributeError:
            raise ImproperlyConfigured("Field %(field)s in the model %(model)s is not a ForeignKey." % {
                "field": self.ml_field_name,
                "model": model.__name__,
            })
    
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        if request.POST.has_key("_addtrans"):
            self.message_user(request, _('The %(name)s "%(obj)s" was added successfully.') % {
                'name': force_unicode(obj._meta.verbose_name),
                'obj': force_unicode(obj),
            })

            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])

            return HttpResponseRedirect(self._construct_trans_url(lang, obj.core)[0])
        else:
            return super(LangDependentModelAdmin, self).response_add(request, obj, post_url_continue)


    def response_change(self, request, obj):
        if request.POST.has_key("_addtrans"):
            self.message_user(request, _('The %(name)s "%(obj)s" was changed successfully.') % {
                'name': force_unicode(obj._meta.verbose_name),
                'obj': force_unicode(obj),
            })

            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])

            return HttpResponseRedirect(self._construct_trans_url(lang, obj.core)[0])
        else:
            return super(LangDependentModelAdmin, self).response_change(request, obj)


    def add_view(self, request, form_url='', extra_context=None):
        trans_links = []

        if request.GET.has_key("core"):
            try:
                obj = self.ml_core_model._default_manager.get(pk=request.GET.get("core"))
            except self.ml_core_model.DoesNotExist:
                obj = None

            if obj:
                trans_links.extend(self._construct_trans_links(obj))

        context = {
            "trans_links": trans_links,
            "trans_langs": settings.LANGUAGES,
            "trans_active_lang": request.GET.get("language", None),
            "trans_core": False,
        }

        context.update(extra_context or {})

        return super(LangDependentModelAdmin, self).add_view(request, form_url, context)


    def change_view(self, request, object_id, extra_context=None):
        try:
            obj = self.model._default_manager.get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None

        trans_links = []
        trans_active_lang = None

        if obj:
            trans_links.extend(self._construct_trans_links(obj.core))
            trans_active_lang = obj.language

        context = {
            "trans_links": trans_links,
            "trans_langs": settings.LANGUAGES,
            "trans_active_lang": trans_active_lang,
            "trans_core": False,
        }

        context.update(extra_context or {})

        return super(LangDependentModelAdmin, self).change_view(request, object_id, context)


class LangAgnosticModelAdmin(MultiLangModelAdmin):
    """
    A subclass of `MultiLangModelAdmin` that should be used for core models 
    that have non-translatable fields and that relate to translatable objects.
    """
    def __init__(self, model, admin_site):
        super(LangAgnosticModelAdmin, self).__init__(model, admin_site)
        
        try:
            field = model._meta.get_field_by_name(self.ml_relation_name)
            
            self.ml_trans_model = field[0].model
            self.ml_core_model = model
        except FieldDoesNotExist:
            raise ImproperlyConfigured("Relation %(rel)s could not be found in the model %(model)s." % {
                "rel": self.ml_relation_name,
                "model": model.__name__,
            })
        except AttributeError:
            raise ImproperlyConfigured("Relation %(rel)s in the model %(model)s is not many-to-one." % {
                "rel": self.ml_relation_name,
                "model": model.__name__,
            })
    
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        if request.POST.has_key("_addtrans"):
            self.message_user(request, _('The %(name)s "%(obj)s" was added successfully.') % {
                'name': force_unicode(obj._meta.verbose_name),
                'obj': force_unicode(obj),
            })

            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])

            return HttpResponseRedirect(self._construct_trans_url(lang, obj)[0])
        else:
            return super(LangAgnosticModelAdmin, self).response_add(request, obj, post_url_continue)


    def response_change(self, request, obj):
        if request.POST.has_key("_addtrans"):
            self.message_user(request, _('The %(name)s "%(obj)s" was changed successfully.') % {
                'name': force_unicode(obj._meta.verbose_name),
                'obj': force_unicode(obj),
            })

            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])

            return HttpResponseRedirect(self._construct_trans_url(lang, obj)[0])
        else:
            return super(LangAgnosticModelAdmin, self).response_change(request, obj)


    def add_view(self, request, form_url='', extra_context=None):
        context = {
            "trans_links": [],
            "trans_langs": settings.LANGUAGES,
            "trans_active_lang": request.GET.get("language", None),
            "trans_core": True,
        }

        context.update(extra_context or {})

        return super(LangAgnosticModelAdmin, self).add_view(request, form_url, context)


    def change_view(self, request, object_id, extra_context=None):
        try:
            obj = self.model._default_manager.get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None

        trans_links = []

        if obj:
            trans_links.extend(self._construct_trans_links(obj))

        context = {
            "trans_links": trans_links,
            "trans_langs": settings.LANGUAGES,
            "trans_active_lang": None,
            "trans_core": True,
        }

        context.update(extra_context or {})

        return super(LangAgnosticModelAdmin, self).change_view(request, object_id, context)
