from django.contrib import admin

from test_app.models import NewsStory


class NewsStoryAdmin(admin.ModelAdmin):
    list_display = ('headline', 'language', 'publication_date')
    list_filter = ('language',)


admin.site.register(NewsStory, NewsStoryAdmin)
