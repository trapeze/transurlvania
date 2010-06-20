from django import template
from django.template.defaultfilters import stringfilter

from django.utils.translation import check_for_language
from django.utils.translation.trans_real import translation

from transurlvania.translators import NoTranslationError


register = template.Library()


def token_splitter(token, unquote=False):
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

    if unquote:
        args = [strip_quotes(arg) for arg in args]

    return {
        'tag_name':tag_name,
        'args':args,
        'context_var':context_var,
    }


def strip_quotes(string):
    """
    Strips quotes off the ends of `string` if it is quoted
    and returns it.
    """
    if len(string) >= 2:
        if string[0] == string[-1]:
            if string[0] in ('"', "'"):
                string = string[1:-1]
    return string


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
    fallback = None
    if len(bits['args']) < 1:
        raise template.TemplateSyntaxError, "%s tag requires at least one argument" % bits['tag_name']
    elif len(bits['args']) == 2:
        fallback = bits['args'][1]
    elif len(bits['args']) > 2:
        raise template.TemplateSyntaxError, "%s tag takes at most two arguments" % bits['tag_name']

    return ThisPageInLangNode(bits['args'][0], fallback, bits['context_var'])


class ThisPageInLangNode(template.Node):
    def __init__(self, lang, fallback=None, context_var=None):
        self.context_var = context_var
        self.lang = template.Variable(lang)
        if fallback:
            self.fallback = template.Variable(fallback)
        else:
            self.fallback = None

    def render(self, context):
        try:
            output = context['_url_translator'].get_url(
                self.lang.resolve(context), context
            )
        except (KeyError, NoTranslationError), e:
            output = ''

        if (not output) and self.fallback:
            output = self.fallback.resolve(context)

        if self.context_var:
            context[self.context_var] = output
            return ''
        else:
            return output


@register.filter
@stringfilter
def trans_in_lang(string, lang):
    """
    Translate a string into a specific language (which can be different
    than the set language).

    Usage:

        {{ var|trans_in_lang:"fr" }}

    """
    if check_for_language(lang):
        return translation(lang).ugettext(string)
    return string
