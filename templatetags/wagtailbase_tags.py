from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.

    :rtype: `wagtail.wagtailcore.models.Page`
    """
    return context['request'].site.root_page


@register.inclusion_tag('wagtailbase/tags/main_menu.html', takes_context=True)
def main_menu(context, root, current_page):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    menu_pages = root.get_children().filter(live=True, show_in_menus=True)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'menu_pages': menu_pages}


@register.inclusion_tag('wagtailbase/tags/local_menu.html', takes_context=True)
def local_menu(context, current_page):
    """Returns the local menu items, the parent and siblings of the current
    page. Only live pages are returned."""
    parent = current_page.index_page
    menu_pages = parent.get_children().filter(live=True)

    return {'request': context['request'], 'current_page': current_page,
            'menu_pages': menu_pages}