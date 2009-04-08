from django.conf import settings


HIDE_TRANSLATABLE_APPS = getattr(settings, "MULTILANG_HIDE_TRANSLATABLE_APPS", False)
