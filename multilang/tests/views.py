from django.views.generic import simple
from django.http import HttpResponse


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
