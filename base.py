from django.db import models
from django.db.models.signals import post_init

from django.http import Http404
from django.core.urlresolvers import RegexURLResolver
from django.conf.urls import url

from wagtail.wagtailadmin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                                PageChooserPanel)
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField


import logging
logger = logging.getLogger(__name__)


class AbstractLinkField(models.Model):

    """Abstract class for link fields."""
    link_document = models.ForeignKey('wagtaildocs.Document', blank=True,
                                      null=True, related_name='+')
    link_external = models.URLField('External link', blank=True, null=True)
    link_page = models.ForeignKey('wagtailcore.Page', blank=True,
                                  null=True, related_name='+')

    panels = [
        DocumentChooserPanel('link_document'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    class Meta:
        abstract = True


class AbstractRelatedLink(AbstractLinkField):

    """Abstract class for related links."""
    title = models.CharField(max_length=256, help_text='Link title')

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(AbstractLinkField.panels, 'Link')
    ]

    class Meta:
        abstract = True


class BasePage(Page):

    """Abstract class Page. This class is not abstract to Django because
    it needs access to the manager. It will not appear in the Wagtail
    admin, however.

    It implements methods to overload routing and serving multiple views
    on a page. Based in the SuperPage class from wagtail here:
    https://gist.github.com/kaedroho/10296244#file-superpage-py

    All pages in wagtailbase inherit from this class."""

    is_abstract = True

    def is_current_or_ancestor(self, page):
        """Returns True if the given page is the current page or is an ancestor
        of the current page."""
        page = page.specific

        if self.id == page.id:
            return True

        parent = self.get_parent().specific

        if parent and isinstance(
                parent, BasePage) and parent.is_current_or_ancestor(page):
            return True

        return False

    def get_subpage_urls(self):
        """
        Override this method to add your own subpage urls
        """
        return [
            url('^$', self.serve, name='main'),
        ]

    def reverse_subpage(self, name, *args, **kwargs):
        """
        This method does the same job as Djangos' built in
        "urlresolvers.reverse()" function for subpage urlconfs.
        """
        resolver = RegexURLResolver(r'^', self.get_subpage_urls())
        return self.url + resolver.reverse(name, *args, **kwargs)

    def resolve_subpage(self, path):
        """
        This finds a view method/function from a URL path.
        """
        logging.debug('resolving subpage with path `{}`'.format(path))
        logging.debug('urls `{}`'.format(self.get_subpage_urls()))
        resolver = RegexURLResolver(r'^', self.get_subpage_urls())
        logging.debug('resolved to `{}`'.format(resolver))
        return resolver.resolve(path)

    def route(self, request, path_components):
        """
        This hooks the subpage urls into Wagtails routing.
        """

        logging.debug('{} route with {}'.format(self, path_components))
        if self.live:
            try:
                path = '/'.join(path_components)
                if path:
                    path += '/'

                view, args, kwargs = self.resolve_subpage(path)
                return view(request, *args, **kwargs)
            except Http404:
                pass

        return super(BasePage, self).route(request, path_components)


def handle_page_post_init(sender, instance, **kwargs):
    """Handler for the post init signal. Sets the Page.show_in_menus default
    value to True."""
    if isinstance(instance, BasePage):
        instance.show_in_menus = True

post_init.connect(handle_page_post_init)


class BaseIndexPage(BasePage):

    """Base class for index pages. Index pages are pages that will have
    children pages."""
    introduction = RichTextField(blank=True)

    indexed_fields = ('introduction', )
    is_abstract = True

    @property
    def children(self):
        """Returns a list of the pages that are children of this page."""
        return self.get_children().filter(live=True)


class BaseRichTextPage(BasePage):

    """Base class for rich text pages."""
    content = RichTextField()

    indexed_fields = ('content', )
    is_abstract = True

    @property
    def index_page(self):
        """Finds and returns the index page from the page ancestors. If no
        index page is found in the ancestors, it returns the first page."""
        for ancestor in reversed(self.get_ancestors()):
            if isinstance(ancestor.specific, BaseIndexPage):
                return ancestor

        # No ancestors are index pages, returns the first page
        return Page.objects.first()
