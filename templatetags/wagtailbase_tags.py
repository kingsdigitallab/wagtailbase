from ..models import BlogPost

from django import template
from django.conf import settings
from django.utils.text import slugify
from django.template.defaultfilters import stringfilter


from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.templatetags.wagtailcore_tags import pageurl

from wagtailbase.util import unslugify


register = template.Library()


@register.inclusion_tag('wagtailbase/tags/breadcrumbs.html',
                        takes_context=True)
def breadcrumbs(context, root, current_page):
    """Returns the pages that are part of the breadcrumb trail of the current
    page, up to the root page."""
    pages = current_page.get_ancestors(
        inclusive=True).descendant_of(root).filter(live=True)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'pages': pages}


@register.assignment_tag(takes_context=False)
def are_comments_allowed():
    """Returns True if commenting on the site is allowed, False otherwise."""
    return getattr(settings, 'ALLOW_COMMENTS', False)


@register.assignment_tag(takes_context=False)
def get_disqus_shortname():
    """Returns the DISCUS shortname setting for comments."""
    return settings.DISQUS_SHORTNAME


@register.assignment_tag(takes_context=True)
def get_request_parameters(context, exclude=None):
    """Returns a string with all the request parameters except the exclude
    parameter."""
    params = ''
    request = context['request']

    for key, value in request.GET.items():
        if key != exclude:
            params += '&{key}={value}'.format(key=key, value=value)

    return params


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.

    :rtype: `wagtail.wagtailcore.models.Page`
    """
    return context['request'].site.root_page


@register.assignment_tag(takes_context=True)
def has_local_menu(context, current_page):
    """Returns True if the current page has a local menu, False otherwise. A
    page has a local menu, if it is not the site root, and if it is not a leaf
    page."""
    site_root = get_site_root(context)

    if current_page.id != site_root.id:
        if current_page.depth <= 4 and not current_page.is_leaf():
            return True
        elif current_page.depth > 4:
            return True

    return False


@register.filter
def is_current_or_ancestor(page, current_page):
    """Returns True if the given page is the current page or is an ancestor of
    the current page."""
    return current_page.is_current_or_ancestor(page)


@register.inclusion_tag('wagtailbase/tags/latest_blog_post.html',
                        takes_context=True)
def latest_blog_post(context, parent=None):
    """Returns the latest blog post that is child of the given parent. If no
    parent is given it defaults to the latest BlogPost object."""
    post = None

    if parent:
        post = parent.get_children().order_by('-date').first()
    else:
        post = BlogPost.objects.all().order_by('-date').first()

    return {'request': context['request'], 'post': post}


@register.inclusion_tag('wagtailbase/tags/local_menu.html', takes_context=True)
def local_menu(context, current_page=None):
    """Retrieves the secondary links for the 'also in this section' links -
    either the children or siblings of the current page."""
    menu_pages = []

    if current_page:
        menu_pages = current_page.get_children().filter(
            live=True, show_in_menus=True)

        # if no children, get siblings instead
        if len(menu_pages) == 0:
            menu_pages = current_page.get_siblings().filter(
                live=True, show_in_menus=True)

    # required by the pageurl tag that we want to use within this template
    return {'request': context['request'], 'current_page': current_page,
            'menu_pages': menu_pages}


@register.inclusion_tag('wagtailbase/tags/main_menu.html', takes_context=True)
def main_menu(context, root, current_page=None):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    menu_pages = root.get_children().filter(live=True, show_in_menus=True)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'menu_pages': menu_pages}


@register.simple_tag(takes_context=True)
def slugurl(context, slug):
    """Returns the URL for the page that has the given slug."""
    page = Page.objects.filter(slug=slug).first()

    if page:
        return pageurl(context, page)
    else:
        return None


@register.simple_tag(takes_context=True)
def archiveurl(context, page, *args):
    """Returns the URL for the page that has the given slug."""
    archive_url = []

    try:
        # is author
        archive_url += ['author', slugify(args[0].username)]
    except AttributeError:
        try:
            # is tag
            archive_url += ['tag', slugify(args[0].name)]
        except AttributeError:
            # date
            archive_url += ['date'] + [str(arg) for arg in args]
    except IndexError:
        archive_url = []

    return pageurl(context, page) + '/'.join(archive_url)


@register.filter(name="unslugify")
@stringfilter
def unslugify_filter(value):
    return unslugify(value)
