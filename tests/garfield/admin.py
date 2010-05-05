from django.contrib import admin

from garfield.models import ComicStrip


class ComicStripAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'publication_date')
    list_filter = ('language',)


admin.site.register(ComicStrip, ComicStripAdmin)
