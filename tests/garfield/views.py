from django.views.generic import simple, list_detail
from django.http import HttpResponse

from garfield.models import ComicStrip


def home(request):
    return simple.direct_to_template(request, 'home.html')


def about_us(request):
    return simple.direct_to_template(request, 'about_us.html')


def landing(request):
    return simple.direct_to_template(request, 'garfield/landing.html')


def the_president(request):
    return simple.direct_to_template(request, 'garfield/the_president.html')


def comic_strip_list(request):
    return list_detail.object_list(
            request,
            queryset=ComicStrip.objects.filter(language=request.LANGUAGE_CODE),
            template_object_name='comic_strip',
            )


def comic_strip_detail(request, strip_id):
    return list_detail.object_detail(
            request,
            ComicStrip.objects.filter(language=request.LANGUAGE_CODE),
            id=strip_id,
            template_object_name='comic_strip',
            )


def jim_davis(request):
    return HttpResponse('Jim Davis is the creator of Garfield')
