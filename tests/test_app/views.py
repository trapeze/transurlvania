from django.views.generic import simple, list_detail
from django.http import HttpResponse

from test_app.models import NewsStory


def multilang_home(request):
    return simple.direct_to_template(request, 'multilang_tests/multilang_home.html')


def home(request):
    return simple.direct_to_template(request, 'multilang_tests/home.html')


def stuff(request):
    return simple.direct_to_template(request, 'multilang_tests/stuff.html')


def things(request):
    return simple.direct_to_template(request, 'multilang_tests/things.html')


def spangles_stars(request):
    return HttpResponse('When you wish...')


def spangles_stripes(request):
    return HttpResponse('A leopard never changes them...')


def spangles_home(request):
    return HttpResponse('Home')


def news_story_detail(request, slug):
    return list_detail.object_detail(
            request,
            NewsStory.objects.all(),
            slug_field='slug',
            slug=slug,
            template_name='multilang_tests/newsstory_detail.html'
            )
