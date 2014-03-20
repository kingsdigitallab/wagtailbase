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

# Retrieves the secondary links for the 'also in this section' links
# - either the children or siblings of the current page
@register.inclusion_tag('wagtailbase/tags/local_menu.html', takes_context=True)
def local_menu(context, current_page=None):
    pages = []
    if current_page:
        pages = current_page.get_children().filter(
            live=True,
            show_in_menus=True
        )

        # If no children, get siblings instead
        if len(pages) == 0:
            pages = current_page.get_other_siblings().filter(
                live=True,
                show_in_menus=True
            )
    return {
        'menu_pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }
