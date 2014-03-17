from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.

    :rtype: `wagtail.wagtailcore.models.Page`
    """
    return 'hello'
