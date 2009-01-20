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
    ml_core = False
    
    
    def __init__(self, model, admin_site):
        super(MultiLangModelAdmin, self).__init__(model, admin_site)
        
        if self.ml_core:
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
        else:
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
            return "../../../%(app)s/%(model)s/%(id)s/" % {
                "app": self.ml_trans_model._meta.app_label,
                "model": self.ml_trans_model.__name__.lower(),
                "id": trans_obj._get_pk_val(),
            }
        else:
            return "../../../%(app)s/%(model)s/add/?language=%(lang)s&core=%(id)s" % {
                "app": self.ml_trans_model._meta.app_label,
                "model": self.ml_trans_model.__name__.lower(),
                "lang": lang,
                "id": obj._get_pk_val(),
            }
    
    
    def _construct_trans_links(self, obj):
        trans_links = []
        
        if not self.ml_core:
            trans_links.append({
                "name": obj,
                "url": self._construct_core_url(obj),
            })
        
        for lang in dict(settings.LANGUAGES):
            trans_links.append({
                "name": dict(settings.LANGUAGES)[lang],
                "url": self._construct_trans_url(lang, obj),
            })
        
        return trans_links
    
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        pk_value = obj._get_pk_val()
        
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {
            'name': force_unicode(opts.verbose_name),
            'obj': force_unicode(obj),
        }
        
        if request.POST.has_key("_addtrans"):
            self.message_user(request, msg)
            
            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])
            
            if self.ml_core:
                return HttpResponseRedirect(self._construct_trans_url(lang, obj))
            else:
                return HttpResponseRedirect(self._construct_trans_url(lang, obj.core))
        else:
            return super(MultiLangModelAdmin, self).response_add(request, obj, post_url_continue)
    
    
    def response_change(self, request, obj):
        opts = obj._meta
        pk_value = obj._get_pk_val()
        
        msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
            'name': force_unicode(opts.verbose_name),
            'obj': force_unicode(obj),
        }
        
        if request.POST.has_key("_addtrans"):
            self.message_user(request, msg)
            
            lang = request.POST.get("_addtrans_lang", settings.LANGUAGES[0][0])
            
            if self.ml_core:
                return HttpResponseRedirect(self._construct_trans_url(lang, obj))
            else:
                return HttpResponseRedirect(self._construct_trans_url(lang, obj.core))
        else:
            return super(MultiLangModelAdmin, self).response_change(request, obj)
    
    
    def add_view(self, request, form_url='', extra_context=None):
        trans_links = []
        
        if request.GET.has_key("core") and not self.ml_core:
            try:
                obj = self.ml_core_model._default_manager.get(pk=request.GET.get("core"))
            except self.ml_core_model.DoesNotExist:
                obj = None
            
            if obj:
                trans_links.extend(self._construct_trans_links(obj))
        
        context = {
            "trans_links": trans_links,
            "trans_langs": settings.LANGUAGES,
        }
        
        context.update(extra_context or {})
        
        return super(MultiLangModelAdmin, self).add_view(request, form_url, context)
    
    
    def change_view(self, request, object_id, extra_context=None):
        try:
            obj = self.model._default_manager.get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None
        
        trans_links = []
        
        if obj:
            if self.ml_core:
                trans_links.extend(self._construct_trans_links(obj))
            else:
                trans_links.extend(self._construct_trans_links(obj.core))
        
        context = {
            "trans_links": trans_links,
            "trans_langs": settings.LANGUAGES,
        }
        
        context.update(extra_context or {})
        
        return super(MultiLangModelAdmin, self).change_view(request, object_id, context)
    
    
    class Media:
        css = {
            "all": ("multilang/css/admin.css",),
        }


class LangDependentModelAdmin(MultiLangModelAdmin):
    """
    A subclass of `MultiLangModelAdmin` that should be used for models that 
    have translatable fields and that link to a core model.
    """
    ml_core = False


class LangAgnosticModelAdmin(MultiLangModelAdmin):
    """
    A subclass of `MultiLangModelAdmin` that should be used for core models 
    that have non-translatable fields and that relate to translatable objects.
    """
    ml_core = True
