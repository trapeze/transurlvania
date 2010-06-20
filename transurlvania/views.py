from django.http import HttpResponseRedirect
from django.utils.translation import get_language_from_request


def detect_language_and_redirect(request):
    return HttpResponseRedirect(
        '/%s/' % get_language_from_request(request)
    )
