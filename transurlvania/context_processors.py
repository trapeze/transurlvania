def translate(request):
    url_translator = getattr(request, 'url_translator', None)
    if url_translator:
        return {'_url_translator': url_translator}
    else:
        return {}