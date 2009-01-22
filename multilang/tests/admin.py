from django.contrib import admin

from multilang.admin import LangDependentModelAdmin, LangAgnosticModelAdmin

from multilang.tests.models import NewsStoryCore, NewsStory


class NewsStoryAdmin(LangDependentModelAdmin):
    list_display = ('headline', 'language',)
    list_filter = ('language',)


class NewsStoryCoreAdmin(LangAgnosticModelAdmin):
    list_display = ('headline', 'pub_date',)


admin.site.register(NewsStory, NewsStoryAdmin)
admin.site.register(NewsStoryCore, NewsStoryCoreAdmin)
