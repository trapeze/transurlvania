from transurlvania.translators import BasicScheme, ObjectBasedScheme, DirectToURLScheme


def translate_using_url(url_name):
    return _translate_using(DirectToURLScheme(url_name))


def translate_using_object(object_name):
    return _translate_using(ObjectBasedScheme(object_name))


def translate_using_custom_scheme(scheme):
    return _translate_using(scheme)


def do_not_translate(view_func):
    return _translate_using(BasicScheme())(view_func)


def _translate_using(scheme):
    def translate_decorator(view_func):
        def inner(request, *args, **kwargs):
            if hasattr(request, 'url_translator'):
                request.url_translator.scheme = scheme
            return view_func(request, *args, **kwargs)
        return inner
    return translate_decorator


def permalink_in_lang(func):
    from transurlvania.urlresolvers import reverse_for_language
    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        return reverse_for_language(bits[0], bits[1], None, *bits[2:4])
    return inner
