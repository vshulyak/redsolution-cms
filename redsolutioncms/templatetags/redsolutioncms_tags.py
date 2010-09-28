from django import template
from django.template import TOKEN_VAR, TOKEN_BLOCK, TOKEN_COMMENT, TOKEN_TEXT, \
    BLOCK_TAG_START, VARIABLE_TAG_START, VARIABLE_TAG_END, BLOCK_TAG_END

register = template.Library()

class RawNode(template.Node):
    def __init__(self, data):
        self.data = data

    def render(self, context):
        return self.data

@register.tag
def raw(parser, token):
    """
    Render as just text everything between ``{% raw %}`` and ``{% endraw %}``.
    """
    ENDRAW = 'endraw'
    data = u''
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == TOKEN_BLOCK and token.contents == ENDRAW:
            return RawNode(data)
        if token.token_type == TOKEN_VAR:
            data += '%s %s %s' % (VARIABLE_TAG_START, token.contents, VARIABLE_TAG_END)
        elif token.token_type == TOKEN_BLOCK:
            data += '%s %s %s' % (BLOCK_TAG_START, token.contents, BLOCK_TAG_END)
        elif token.token_type == TOKEN_COMMENT:
            pass # django.template don`t save comments
        elif token.token_type == TOKEN_TEXT:
            data += token.contents
    parser.unclosed_block_tag([ENDRAW])

@register.simple_tag
def start_block():
    return u'{%'

@register.simple_tag
def end_block():
    return u'%}'
