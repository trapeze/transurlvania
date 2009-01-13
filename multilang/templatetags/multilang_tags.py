from django import template

from multilang.translators import NoTranslationError

register = template.Library()


@register.tag
def this_page_in_lang(parser, token):
    """
    Returns the URL for the equivalent of the current page in the requested language.
    If no URL can be generated, returns nothing.
    
    Usage:
        
        {% this_page_in_lang "fr" %}
    
    """
    try:
        tag_name, lang = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % tag_name
    return ThisPageInLangNode(lang)


class ThisPageInLangNode(template.Node):
    def __init__(self, lang):
        self.lang = template.Variable(lang)

    def render(self, context):
        try:
            return context['_url_translator'].get_url(self.lang.resolve(context),
                                                      context)
        except (KeyError, NoTranslationError), e:
            return ''
