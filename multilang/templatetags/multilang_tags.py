from django import template

from multilang.translators import NoTranslationError

register = template.Library()


def token_splitter(token):
    """
    Splits a template tag token and returns a dict containing:
    * tag_name  - The template tag name (ie. first piece in the token)
    * args      - List of arguments to the template tag
    * context_var - Context variable name if the "as" keyword is used,
                    or None otherwise.
    """
    pieces = token.split_contents()

    tag_name = pieces[0]
    args = []
    context_var = None
    if len(pieces) > 2 and pieces[-2] == 'as':
        args = pieces[1:-2]
        context_var = pieces[-1]
    elif len(pieces) > 1:
        args = pieces[1:]

    return {
        'tag_name':tag_name,
        'args':args,
        'context_var':context_var,
    }


@register.tag
def this_page_in_lang(parser, token):
    """
    Returns the URL for the equivalent of the current page in the requested language.
    If no URL can be generated, returns nothing.

    Usage:

        {% this_page_in_lang "fr" %}
        {% this_page_in_lang "fr" as var_name %}

    """

    bits = token_splitter(token)
    if len(bits['args']) != 1:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % tag_name
    return ThisPageInLangNode(bits['args'][0], bits['context_var'])


class ThisPageInLangNode(template.Node):
    def __init__(self, lang, context_var=None):
        self.context_var = context_var
        self.lang = template.Variable(lang)

    def render(self, context):
        try:
            output = context['_url_translator'].get_url(
                self.lang.resolve(context), context
            )
        except (KeyError, NoTranslationError), e:
            output = ''

        if self.context_var:
            context[self.context_var] = output
            return ''
        else:
            return output
