from django import template
from django.utils import translation

from multilang.translators import NoTranslationError


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


@register.tag
def trans_in_lang(parser, token):
    """
    Translate a string in a specific language (which can be different
    than the set language).

    Usage:

        {% trans_in_lang "some word" "fr" %}
        {% trans_in_lang "some word" "fr" as var_name %}

    """
    bits = token_splitter(token, unquote=True)
    if len(bits['args']) != 2:
        raise template.TemplateSyntaxError, "%s tag requires two arguments" % tag_name

    return TransInLangNode(bits['args'][0], bits['args'][1],
        bits['context_var']
    )


class TransInLangNode(template.Node):
    def __init__(self, string, lang, context_var=None):
        self.string = string
        self.lang = lang
        self.context_var = context_var

    def render(self, context):
        try:
            string = template.Variable(self.string).resolve(context)
        except template.VariableDoesNotExist:
            string = self.string
        try:
            lang = template.Variable(self.lang).resolve(context)
        except template.VariableDoesNotExist:
            lang = self.lang

        output = string
        if translation.check_for_language(lang):
            current_lang = translation.get_language()
            translation.activate(lang)
            output = translation.ugettext(string)
            translation.activate(current_lang)

        if self.context_var:
            context[self.context_var] = output
            return ''
        else:
            return output
