import markdown2

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def render_markdown(value):
    safe_source = escape(value or '')
    html = markdown2.markdown(
        safe_source,
        extras=['fenced-code-blocks', 'tables', 'strike', 'break-on-newline'],
    )
    return mark_safe(html)
